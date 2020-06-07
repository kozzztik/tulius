import logging

from django.db.models.query_utils import Q

from tulius.forum import models as forum_models
from tulius.forum.rights import base
from tulius.forum.rights import default
from tulius.games import models as game_models
from tulius.games.models import GameGuest, GAME_STATUS_FINISHING
from tulius.forum.rights.plugin import RightsPlugin
from tulius.stories import models as stories_models
from .forms import GameRightForm
from . import models


class GameRightsPlugin(RightsPlugin):
    # pylint: disable=too-many-branches
    def strict_roles(self, thread):
        sm = self.site.models
        if not thread.parent_id:
            thread.strict_read = [] if (
                thread.access_type == self.models.THREAD_ACCESS_TYPE_NO_READ
            ) else None
            thread.strict_write = [] if (
                thread.access_type >= sm.THREAD_ACCESS_TYPE_NO_WRITE
            ) else None
        else:
            thread.strict_read = [
                value for value in thread.parent.strict_read
            ] if thread.parent.strict_read is not None else None
            thread.strict_write = [
                value for value in thread.parent.strict_write
            ] if thread.parent.strict_write is not None else None
            if (thread.access_type >= sm.THREAD_ACCESS_TYPE_NO_WRITE) and (
                    thread.strict_write is None):
                thread.strict_write = []
        rights = self.site.gamemodels.GameThreadRight.objects.filter(
            thread_id=thread.id).distinct()
        rights = rights.select_related('role')
        read_roles = [
            right.role for right in rights
            if right.access_level & sm.THREAD_ACCESS_READ]
        write_roles = [
            right.role for right in rights
            if right.access_level & sm.THREAD_ACCESS_WRITE]
        if thread.access_type == sm.THREAD_ACCESS_TYPE_NO_READ:
            if thread.strict_read is None:
                thread.strict_read = read_roles
            else:
                thread.strict_read = [
                    role for role in thread.strict_read if role in read_roles]
        if (thread.access_type == sm.THREAD_ACCESS_TYPE_NOT_SET) and (
                thread.strict_write is not None):
            for role in write_roles:
                if role not in thread.strict_write:
                    thread.strict_write += [role]
        if thread.access_type == sm.THREAD_ACCESS_TYPE_OPEN:
            thread.strict_write = thread.strict_read
        if thread.access_type >= sm.THREAD_ACCESS_TYPE_NO_WRITE:
            for role in write_roles:
                if role not in thread.strict_write:
                    thread.strict_write += [role]
        # fix:thread author can write and read
        if thread.data1 and ((thread.strict_read is not None) or (
                thread.strict_write is not None)):
            role = stories_models.Role.objects.get(id=thread.data1)
            if thread.strict_read is not None:
                if role not in thread.strict_read:
                    thread.strict_read += [role]
            if thread.strict_write is not None:
                if role not in thread.strict_write:
                    thread.strict_write += [role]

    def get_parent_rights(self, thread, user):
        if not thread.parent_id:
            variations = stories_models.Variation.objects.filter(thread=thread)
            if not variations:
                logger = logging.getLogger('django.request')
                logger.fatal('Game thread %s have no variation', thread.id)
                raise Exception('game post have no variation')
            thread.variation = variations[0]
            thread.game = thread.variation.game
            thread.admin = thread.variation.edit_right(user)
            thread.guest = False
            self.strict_roles(thread)
            if not user.is_anonymous:
                if (not thread.admin) and thread.game:
                    guests = GameGuest.objects.filter(
                        game=thread.game, user=user)
                    if guests:
                        thread.guest = True
                thread.user_roles = stories_models.Role.objects.filter(
                    variation=thread.variation, user=user).values('id')
                thread.user_roles = [role['id'] for role in thread.user_roles]
            else:
                thread.user_roles = []
                thread.user_accesed_roles = []
            if thread.admin:
                return True, True, True
            if not thread.game:
                return False, False, False
            parent_read = thread.game.read_right(user)
            parent_write = thread.game.write_right(user)
            return parent_read, parent_write, False
        (parent_read, parent_write, parent_moderate) = super(
            GameRightsPlugin, self).get_parent_rights(thread, user)
        thread.variation = thread.parent.variation
        thread.game = thread.parent.game
        thread.admin = thread.parent.admin
        thread.guest = thread.parent.guest
        thread.user_roles = thread.parent.user_roles
        self.strict_roles(thread)
        return parent_read, parent_write, parent_moderate

    def get_special_rights(self, thread, user):
        special_read = False
        special_write = False
        special_moderate = False
        sm = self.site.models
        if (not user.is_anonymous) and (
                thread.room or (
                    thread.access_type > sm.THREAD_ACCESS_TYPE_NOT_SET)):
            rights = models.GameThreadRight.objects.filter(
                thread=thread, role_id__in=thread.user_roles)
            for right in rights:
                if right.access_level & sm.THREAD_ACCESS_READ:
                    special_read = True
                if right.access_level & sm.THREAD_ACCESS_WRITE:
                    special_write = True
                if right.access_level & sm.THREAD_ACCESS_MODERATE:
                    special_moderate = True
        return special_read, special_write, special_moderate

    def is_superuser_equal(self, thread, user, parent_moderate):
        return super(GameRightsPlugin, self).is_superuser_equal(
            thread, user, parent_moderate) or thread.admin

    def get_rights(self, thread):
        user = thread.view_user
        (read_right, view_right, write_right, edit_right, move_right,
         moderate_right) = super(GameRightsPlugin, self).get_rights(thread)
        if thread.data1 in thread.user_roles:
            read_right = True
            view_right = True
            write_right = True
            edit_right = True
        if thread.guest:
            read_right = True
            write_right = False
            view_right = True
        if thread.game:
            if thread.game.status > GAME_STATUS_FINISHING:
                edit_right = False
                write_right = False
            if thread.game.status >= GAME_STATUS_FINISHING:
                view_right = thread.game.read_right(
                    user) and (not thread.deleted)
                read_right = view_right and (not thread.deleted)
        move_right = moderate_right
        return (
            read_right, view_right, write_right, edit_right, move_right,
            moderate_right)

    def limited_read_list(self, thread):
        persons = [
            right.role for right in
            models.GameThreadRight.objects.filter(thread=thread)]
        if thread.parent and thread.parent.limited_read:
            parent_list = thread.parent.limited_read_list
            persons = [person for person in persons if person in parent_list]
        return persons

    def get_free_descendants(self, thread):
        site_models = self.site.models
        query = Q(access_type__lt=site_models.THREAD_ACCESS_TYPE_NO_READ)
        if thread and thread.user_roles:
            query = query | Q(data1__in=thread.user_roles)
        return site_models.Thread.objects.get_descendants(thread).filter(
            deleted=False).filter(query)

    def read_all(self, thread):
        return thread.game and thread.game.status >= GAME_STATUS_FINISHING

    def get_readeable_protected_descendants(self, thread):
        user = thread.view_user
        site_models = self.site.models
        if user.is_superuser or thread.admin or thread.guest or self.read_all(
                thread):
            threads = site_models.Thread.objects.get_descendants(
                thread
            ).filter(
                deleted=False,
                access_type=site_models.THREAD_ACCESS_TYPE_NO_READ)
            if thread and thread.user_roles:
                threads = threads.exclude(data1__in=thread.user_roles)
            return threads
        rights = models.GameThreadRight.objects.filter(
            role_id__in=thread.user_roles,
            thread__tree_id=thread.tree_id,
            thread__lft__gt=thread.lft,
            thread__rght__lt=thread.rght,
            access_level__gte=site_models.THREAD_ACCESS_READ,
            thread__deleted=False)
        if thread and thread.user_roles:
            rights = rights.exclude(thread__data1__in=thread.user_roles)
        rights = rights.select_related('thread')
        return [right.thread for right in rights]

    def get_free_childs(self, thread):
        site_models = self.site.models
        query = Q(access_type__lt=site_models.THREAD_ACCESS_TYPE_NO_READ)
        if thread and thread.user_roles:
            query = query | Q(data1__in=thread.user_roles)
        query = Q(parent=thread) & query
        return site_models.Thread.objects.filter(query)

    def get_readeable_protected_childs(self, thread):
        user = thread.view_user
        site_models = self.site.models
        if user.is_superuser or thread.admin or self.read_all(thread):
            return site_models.Thread.objects.filter(
                parent=thread,
                access_type=site_models.THREAD_ACCESS_TYPE_NO_READ)
        if user.is_anonymous:
            return []
        query = Q(
            thread__parent=thread,
            thread__access_type=site_models.THREAD_ACCESS_TYPE_NO_READ,
            access_level__gte=site_models.THREAD_ACCESS_READ,
            role_id__in=thread.user_roles)
        query = query & (Q(thread__deleted=False) | Q(
            thread__data1__in=thread.user_roles))
        rights = site_models.GameThreadRight.objects.filter(query)
        rights = rights.select_related('thread')
        return [right.thread for right in rights]

    def get_moderators(self, thread):
        rights = models.GameThreadRight.objects.filter(
            thread_id=thread.id,
            access_level__gt=self.site.models.THREAD_ACCESS_MODERATE)
        rights = rights.select_related('role')
        return [right.role for right in rights]

    def get_accessed_users(self, thread):
        rights = models.GameThreadRight.objects.filter(
            thread_id=thread.id).distinct()
        rights = rights.select_related('role')
        roles = [right.role for right in rights if right.role]
        if not thread.moderate_right():
            roles = [role for role in roles if role.show_in_character_list]
        if thread.strict_read:
            roles = [role for role in roles if role in thread.strict_read]
        return roles

    def init_core(self):
        super(GameRightsPlugin, self).init_core()
        self.core['right_model'] = models.GameThreadRight
        self.core['right_form'] = GameRightForm


class GameRights(base.RightsDescriptor):
    strict_read = None
    strict_write = None
    moderator_roles = None
    admin = False
    guest = False
    user_roles = None


class RightsChecker(default.DefaultRightsChecker):
    _base_rights_class = GameRights
    _rights: GameRights = None
    variation = None

    def __init__(self, variation, thread, user, parent_rights=None):
        self.variation = variation
        super(RightsChecker, self).__init__(
            thread, user, parent_rights=parent_rights)

    def _create_checker(self, thread, parent_rights=None):
        return self.__class__(
            self.variation, thread, self.user, parent_rights=parent_rights)

    def get_rights_for_root(self):
        rights = GameRights()
        if self.thread.id != self.variation.thread_id:
            return rights
        rights.admin = self.variation.edit_right(self.user)
        rights.guest = False
        self.strict_roles(rights)
        if not self.user.is_anonymous:
            if (not rights.admin) and self.variation.game:
                guests = game_models.GameGuest.objects.filter(
                    game=self.variation.game, user=self.user)
                if guests:
                    rights.guest = True
            rights.user_roles = stories_models.Role.objects.filter(
                variation=self.variation, user=self.user).values('id')
            rights.user_roles = [role['id'] for role in
                                 rights.user_roles]
        else:
            rights.user_roles = []
            rights.user_accessed_roles = []
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
        self.strict_roles(self._rights)
        rights = super(RightsChecker, self)._get_rights()
        if self.thread.data1 in rights.user_roles:
            rights.read = True
            rights.write = True
            rights.edit = True
        if rights.guest:
            rights.read = True
        if self.variation.game:
            if self.variation.game.status > GAME_STATUS_FINISHING:
                rights.edit = False
                rights.write = False
            if self.variation.game.status >= GAME_STATUS_FINISHING:
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

    def limited_read_list(self):
        return self._rights.strict_read

    def _get_free_descendants(self):
        query = Q(access_type__lt=forum_models.THREAD_ACCESS_TYPE_NO_READ)
        if self.thread and self._rights.user_roles:
            query = query | Q(data1__in=self._rights.user_roles)
        return forum_models.Thread.objects.get_descendants(self.thread).filter(
            deleted=False).filter(query)

    def _read_all(self):
        return self.variation.game and self.variation.game.status >= \
            GAME_STATUS_FINISHING

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
