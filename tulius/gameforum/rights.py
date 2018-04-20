from django.db.models.query_utils import Q

from tulius.games.models import GameGuest, GAME_STATUS_FINISHING
from tulius.forum.rights.plugin import RightsPlugin
from .forms import GameRightForm
from . import models


class GameRightsPlugin(RightsPlugin):
    def strict_roles(self, thread):
        if not thread.parent_id:
            thread.strict_read = [] if (
                thread.access_type == self.models.THREAD_ACCESS_TYPE_NO_READ
            ) else None
            thread.strict_write = [] if (
                thread.access_type >= models.THREAD_ACCESS_TYPE_NO_WRITE
            ) else None
        else:
            thread.strict_read = [
                value for value in thread.parent.strict_read
            ] if thread.parent.strict_read is not None else None
            thread.strict_write = [
                value for value in thread.parent.strict_write
            ] if thread.parent.strict_write is not None else None
            if (thread.access_type >= models.THREAD_ACCESS_TYPE_NO_WRITE) and (
                    thread.strict_write is None):
                thread.strict_write = []
        rights = models.GameThreadRight.objects.filter(
            thread_id=thread.id).distinct()
        rights = rights.select_related('role')
        read_roles = [
            right.role for right in rights
            if right.access_level & models.THREAD_ACCESS_READ]
        write_roles = [
            right.role for right in rights
            if right.access_level & models.THREAD_ACCESS_WRITE]
        if thread.access_type == models.THREAD_ACCESS_TYPE_NO_READ:
            if thread.strict_read is None:
                thread.strict_read = read_roles
            else:
                thread.strict_read = [
                    role for role in thread.strict_read if role in read_roles]
        if (thread.access_type == models.THREAD_ACCESS_TYPE_NOT_SET) and (
                thread.strict_write is not None):
            for role in write_roles:
                if role not in thread.strict_write:
                    thread.strict_write += [role]
        if (thread.access_type == models.THREAD_ACCESS_TYPE_OPEN):
            thread.strict_write = thread.strict_read
        if (thread.access_type >= models.THREAD_ACCESS_TYPE_NO_WRITE):
            for role in write_roles:
                if role not in thread.strict_write:
                    thread.strict_write += [role]
        # fix:thread author can write and read
        if thread.data1 and ((thread.strict_read is not None) or (
                thread.strict_write is not None)):
            role = models.Role.objects.get(id=thread.data1)
            if thread.strict_read is not None:
                if role not in thread.strict_read:
                    thread.strict_read += [role]
            if thread.strict_write is not None:
                if role not in thread.strict_write:
                    thread.strict_write += [role]
    
    def get_parent_rights(self, thread, user):
        if not thread.parent_id:
            variations = models.Variation.objects.filter(thread=thread)
            if variations:
                thread.variation = variations[0]
            else:
                import logging
                logger = logging.getLogger('django.request')
                logger.fatal('Game thread %s have no variation' % (thread.id,))
                raise Exception('game post have no variation')
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
                thread.user_roles = models.Role.objects.filter(
                    variation=thread.variation, user=user).values('id')
                thread.user_roles = [role['id'] for role in thread.user_roles]
            else:
                thread.user_roles = []
                thread.user_accesed_roles = []
            if thread.admin:
                return (True, True, True)
            if not thread.game:
                return (False, False, False)
            parent_read = thread.game.read_right(user)
            parent_write = thread.game.write_right(user) 
            return (parent_read, parent_write, False)
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
        if (not user.is_anonymous) and (
                thread.room or (
                thread.access_type > models.THREAD_ACCESS_TYPE_NOT_SET)):
            rights = models.GameThreadRight.objects.filter(
                thread=thread, role_id__in=thread.user_roles)
            for right in rights:
                if right.access_level & models.THREAD_ACCESS_READ:
                    special_read = True
                if right.access_level & models.THREAD_ACCESS_WRITE:
                    special_write = True
                if right.access_level & models.THREAD_ACCESS_MODERATE:
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
        query = Q(access_type__lt=models.THREAD_ACCESS_TYPE_NO_READ)
        if thread and thread.user_roles:
            query = query | Q(data1__in=thread.user_roles)
        return models.Thread.objects.get_descendants(thread).filter(
            deleted=False).filter(query)
    
    def read_all(self, thread):
        return thread.game and thread.game.status >= GAME_STATUS_FINISHING
    
    def get_readeable_protected_descendants(self, thread):
        user = thread.view_user
        if user.is_superuser or thread.admin or thread.guest or self.read_all(
                thread):
            threads = models.Thread.objects.get_descendants(thread).filter(
                deleted=False, access_type=models.THREAD_ACCESS_TYPE_NO_READ)
            if thread and thread.user_roles:
                threads = threads.exclude(data1__in=thread.user_roles)
            return threads
        else:
            rights = models.GameThreadRight.objects.filter(
                role_id__in=thread.user_roles,
                thread__tree_id=thread.tree_id,
                thread__lft__gt=thread.lft,
                thread__rght__lt=thread.rght,
                access_level__gte=models.THREAD_ACCESS_READ,
                thread__deleted=False)
            if thread and thread.user_roles:
                rights = rights.exclude(thread__data1__in=thread.user_roles)
            rights = rights.select_related('thread')
            return [right.thread for right in rights]
    
    def get_free_childs(self, thread):
        query = Q(access_type__lt=models.THREAD_ACCESS_TYPE_NO_READ)
        if thread and thread.user_roles:
            query = query | Q(data1__in=thread.user_roles)
        query = Q(parent=thread) & query
        return models.Thread.objects.filter(query)
    
    def get_readeable_protected_childs(self, thread):
        user = thread.view_user
        if user.is_superuser or thread.admin or self.read_all(thread):
            return models.Thread.objects.filter(
                parent=thread, access_type=models.THREAD_ACCESS_TYPE_NO_READ)
        else:
            if user.is_anonymous:
                return []
            query = Q(
                thread__parent=thread,
                thread__access_type=models.THREAD_ACCESS_TYPE_NO_READ,
                access_level__gte=models.THREAD_ACCESS_READ,
                role_id__in=thread.user_roles)
            query = query & (Q(thread__deleted=False) | Q(
                thread__data1__in=thread.user_roles))
            rights = models.GameThreadRight.objects.filter(query)
            rights = rights.select_related('thread')
            return [right.thread for right in rights]
        
    def get_moderators(self, thread):
        rights = models.GameThreadRight.objects.filter(
            thread_id=thread.id,
            access_level__gt=models.THREAD_ACCESS_MODERATE)
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
