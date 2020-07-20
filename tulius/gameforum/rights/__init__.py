from django.db.models.query_utils import Q

from tulius.forum import models as forum_models
from tulius.forum.rights import base
from tulius.forum.rights import default
from tulius.games import models as game_models
from tulius.stories import models as stories_models
from tulius.gameforum import models


class GameRights(base.RightsDescriptor):
    strict_read = None
    strict_write = None
    moderator_roles = None
    admin = False
    guest = False
    user_roles = None
    user_write_roles = None
    all_roles = {}

    def __init__(self):
        self.user_roles = []
        self.moderator_roles = []

    def to_json(self):
        result = super(GameRights, self).to_json()
        result['strict_read'] = self.strict_read
        result['user_write_roles'] = self.user_write_roles
        return result


class RightsChecker(default.DefaultRightsChecker):
    _base_rights_class = GameRights
    _rights: GameRights = None
    variation = None

    def __init__(self, variation, thread, user, parent_rights=None):
        self.variation = variation
        super(RightsChecker, self).__init__(
            thread, user, parent_rights=parent_rights)

    def _create_checker(self, thread):
        return self.__class__(self.variation, thread, self.user)

    def get_rights_for_root(self):
        rights = GameRights()
        if self.thread.id != self.variation.thread_id:
            return rights
        rights.admin = self.variation.edit_right(self.user)
        rights.guest = False
        rights.all_roles = {
            role.id: role for role in stories_models.Role.objects.filter(
                variation=self.variation)}
        if not self.user.is_anonymous:
            if (not rights.admin) and self.variation.game:
                guests = game_models.GameGuest.objects.filter(
                    game=self.variation.game, user=self.user)
                if guests:
                    rights.guest = True
            rights.user_roles = [
                k for k, v in rights.all_roles.items() if v.user == self.user]
        else:
            rights.user_roles = []
        self.strict_roles(rights)
        if rights.admin:
            rights.read = True
            rights.write = True
            rights.moderate = True
            return rights
        if not self.variation.game:
            return rights
        # TODO optimize it. roles loaded twice
        rights.read = self.variation.game.read_right(self.user)
        rights.write = self.variation.game.write_right(self.user)
        return rights

    def _get_rights(self):
        if self.thread.parent_id is None:
            return self.get_rights_for_root()
        rights = self._rights = GameRights()
        parent_rights = self.get_parent_rights()
        rights.admin = parent_rights.admin
        rights.guest = parent_rights.guest
        rights.user_roles = parent_rights.user_roles
        rights.all_roles = parent_rights.all_roles
        self.strict_roles(self._rights)
        rights = super(RightsChecker, self)._get_rights()
        if self.thread.data1 in rights.user_roles:
            rights.read = True
            rights.write = True
            rights.edit = True
        if rights.guest:
            rights.read = True
        if self.variation.game:
            if self.variation.game.status > game_models.GAME_STATUS_FINISHING:
                rights.edit = False
                rights.write = False
            if self.variation.game.status >= game_models.GAME_STATUS_FINISHING:
                rights.read = self.variation.game.read_right(
                    self.user) and (not self.thread.deleted)
        rights.move = rights.moderate
        return rights

    def strict_roles(self, rights: GameRights):
        if not self.thread.parent_id:
            rights.strict_read = [] if (
                self.thread.access_type ==
                forum_models.THREAD_ACCESS_TYPE_NO_READ
            ) else None
            rights.strict_write = [] if (
                self.thread.access_type >=
                forum_models.THREAD_ACCESS_TYPE_NO_WRITE
            ) else None
            rights.moderator_roles = []
        else:
            parent_rights = self.get_parent_rights()
            rights.strict_read = parent_rights.strict_read.copy() \
                if parent_rights.strict_read is not None else None
            rights.strict_write = parent_rights.strict_write.copy() \
                if parent_rights.strict_write is not None else None
            if (self.thread.access_type >=
                    forum_models.THREAD_ACCESS_TYPE_NO_WRITE) and (
                        rights.strict_write is None):
                rights.strict_write = []
            rights.moderator_roles = parent_rights.moderator_roles.copy()
        self._process_granted_rights(rights)
        self._process_author_rights(rights)
        rights.user_write_roles = self._process_user_write_roles(rights)

    def _process_granted_rights(self, rights: GameRights):
        granted_rights = models.GameThreadRight.objects.filter(
            thread_id=self.thread.id).distinct()
        read_roles = [
            right.role_id for right in granted_rights
            if right.access_level & forum_models.THREAD_ACCESS_READ]
        write_roles = [
            right.role_id for right in granted_rights
            if right.access_level & forum_models.THREAD_ACCESS_WRITE]
        for right in granted_rights:
            if (right.access_level & forum_models.THREAD_ACCESS_MODERATE) and (
                    right.role_id not in rights.moderator_roles):
                rights.moderator_roles.append(right.role_id)
        if self.thread.access_type == forum_models.THREAD_ACCESS_TYPE_NO_READ:
            if rights.strict_read is None:
                rights.strict_read = read_roles
            else:
                rights.strict_read = [
                    role for role in rights.strict_read if role in read_roles]
        if (self.thread.access_type ==
                forum_models.THREAD_ACCESS_TYPE_NOT_SET) and (
                    rights.strict_write is not None):
            for role in write_roles:
                if role not in rights.strict_write:
                    rights.strict_write += [role]
        if self.thread.access_type == forum_models.THREAD_ACCESS_TYPE_OPEN:
            rights.strict_write = rights.strict_read
        if self.thread.access_type >= forum_models.THREAD_ACCESS_TYPE_NO_WRITE:
            for role in write_roles:
                if role not in rights.strict_write:
                    rights.strict_write += [role]

    def _process_author_rights(self, rights: GameRights):
        # thread author can write and read
        if not self.thread.data1:
            return
        role = self.thread.data1
        if (rights.strict_read is not None) and (
                role not in rights.strict_read):
            rights.strict_read += [role]
        if (rights.strict_write is not None) and (
                role not in rights.strict_write):
            rights.strict_write += [role]

    def _process_user_write_roles(self, rights):
        if rights.admin or not self.variation.game:
            return [None] + list(rights.all_roles.keys())
        if rights.strict_write is None:
            return rights.user_roles
        return [pk for pk in rights.user_roles if pk in rights.strict_write]

    def get_granted_rights(self):
        rights = self._rights
        self.strict_roles(rights)
        read = False
        write = False
        moderate = False
        if self.user.is_anonymous:
            return read, write, moderate
        if (not self.thread.room) and (
                self.thread.access_type ==
                forum_models.THREAD_ACCESS_TYPE_NOT_SET):
            return read, write, moderate
        for role in rights.user_roles:
            if rights.moderator_roles and (role in rights.moderator_roles):
                moderate = True
            if rights.strict_write and (role in rights.strict_write):
                write = True
            if rights.strict_read and (role in rights.strict_read):
                read = True
        return read, write, moderate

    def get_moderators_and_accessed_users(self):
        return self._rights.moderator_roles or [], self._rights.strict_read

    def get_limited_read_list(self, parent_rights):
        return parent_rights.strict_read

    def _get_free_descendants(self):
        query = Q(access_type__lt=forum_models.THREAD_ACCESS_TYPE_NO_READ)
        if self.thread and self._rights.user_roles:
            query = query | Q(data1__in=self._rights.user_roles)
        return forum_models.Thread.objects.get_descendants(self.thread).filter(
            deleted=False).filter(query)

    def _read_all(self):
        return self.variation.game and self.variation.game.status >= \
            game_models.GAME_STATUS_FINISHING

    def _get_readable_protected_descendants(self):
        user = self.user
        r = self._rights
        if user.is_superuser or r.admin or r.guest or self._read_all():
            threads = forum_models.Thread.objects.get_descendants(
                self.thread
            ).filter(
                deleted=False,
                access_type=forum_models.THREAD_ACCESS_TYPE_NO_READ)
            if self.thread and r.user_roles:
                threads = threads.exclude(data1__in=r.user_roles)
            return threads
        rights = models.GameThreadRight.objects.filter(
            role_id__in=r.user_roles,
            thread__tree_id=self.thread.tree_id,
            thread__lft__gt=self.thread.lft,
            thread__rght__lt=self.thread.rght,
            access_level__gte=forum_models.THREAD_ACCESS_READ,
            thread__deleted=False)
        if r.user_roles:
            rights = rights.exclude(thread__data1__in=r.user_roles)
        rights = rights.select_related('thread')
        return [right.thread for right in rights]
