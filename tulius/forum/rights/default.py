from django.db.models.query_utils import Q

from tulius.forum.threads import models as thread_models
from tulius.forum.rights import models
from tulius.forum.rights import base


class DefaultRightsChecker(base.BaseThreadRightsChecker):
    _base_rights_class = base.RightsDescriptor
    rights_model = models.ThreadAccessRight
    thread_model = thread_models.Thread

    def get_limited_read_list(self, parent_rights):
        persons = [
            right.user for right in
            self.rights_model.objects.filter(thread=self.thread)]
        if self.thread.user not in persons:
            # owner have access too
            persons.append(self.thread.user)
        if parent_rights.limited_read is not None:
            persons = [p for p in persons if p in parent_rights.limited_read]
        return persons

    def get_granted_rights(self):
        read = False
        write = False
        moderate = False
        if self.user.is_anonymous:
            return read, write, moderate
        if (not self.thread.room) and (
                self.thread.access_type ==
                thread_models.THREAD_ACCESS_TYPE_NOT_SET):
            return read, write, moderate
        rights = self.rights_model.objects.filter(
            thread=self.thread, user=self.user)
        for right in rights:
            if right.access_level & models.THREAD_ACCESS_READ:
                read = True
            if right.access_level & models.THREAD_ACCESS_WRITE:
                write = True
            if right.access_level & models.THREAD_ACCESS_MODERATE:
                moderate = True
        return read, write, moderate

    def get_rights_for_root(self):
        rights = self._base_rights_class()
        rights.read = True
        rights.write = True
        rights.edit = self.user.is_superuser
        rights.moderate = self.user.is_superuser
        return rights

    def _get_rights(self):
        rights = self._rights = self._rights or self._base_rights_class()
        author = (not self.user.is_anonymous) and (
            (self.user.id == self.thread.user_id) or self.user.is_superuser)
        parent_rights = self.get_parent_rights()
        if self.thread.access_type == thread_models.THREAD_ACCESS_TYPE_NO_READ:
            rights.limited_read = self.get_limited_read_list(parent_rights)
        else:
            rights.limited_read = parent_rights.limited_read
        is_superuser_equal = self.user.is_superuser or parent_rights.moderate
        if is_superuser_equal:
            grant_read, grant_write, grant_moderate = True, True, True
        else:
            grant_read, grant_write, grant_moderate = \
                self.get_granted_rights()
        rights.moderate = parent_rights.moderate or grant_moderate
        rights.read = grant_read or grant_moderate or author or (
            self.thread.access_type < thread_models.THREAD_ACCESS_TYPE_NO_READ)
        rights.read = rights.read and parent_rights.read
        if self.thread.access_type == thread_models.THREAD_ACCESS_TYPE_NOT_SET:
            rights.write = parent_rights.write
        else:
            rights.write = (
                self.thread.access_type <
                thread_models.THREAD_ACCESS_TYPE_NO_WRITE)
        rights.write = author or rights.write or grant_write or rights.moderate
        rights.edit = author or rights.moderate
        if self.thread.closed or self.user.is_anonymous:
            rights.write = False
        if self.thread.deleted:
            rights.read = author or rights.moderate
            rights.write = False
            rights.edit = rights.moderate
        rights.move = rights.edit
        return rights

    def get_moderators_and_accessed_users(self):
        rights = self.rights_model.objects.filter(
            thread=self.thread).select_related('user').distinct()
        moderators = [
            right.user for right in rights
            if right.access_level >= models.THREAD_ACCESS_MODERATE]
        return moderators, self._rights.limited_read

    def _get_free_descendants(self):
        query = Q(access_type__lt=thread_models.THREAD_ACCESS_TYPE_NO_READ)
        if self.thread and self.user.is_authenticated:
            query = query | Q(user=self.user)
        return self.thread_model.objects.get_descendants(self.thread).filter(
            query).filter(deleted=False)

    def _get_readable_protected_descendants(self):
        if self.user.is_anonymous or not self.thread.protected_threads:
            return []
        if self.user.is_superuser:
            return self.thread_model.objects.get_descendants(
                self.thread
            ).filter(
                access_type=thread_models.THREAD_ACCESS_TYPE_NO_READ,
                deleted=False)
        rights = self.rights_model.objects.filter(
            user=self.user, thread__tree_id=self.thread.tree_id,
            thread__lft__gt=self.thread.lft, thread__rght__lt=self.thread.rght,
            access_level__gte=models.THREAD_ACCESS_READ,
            thread__deleted=False)
        rights = rights.select_related('thread')
        return [right.thread for right in rights]
