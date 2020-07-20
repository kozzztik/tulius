from django.db.models.query_utils import Q

# TODO: fix this when module moved
from tulius.forum.plugins import ForumPlugin
from .forms import ThreadAccessRightForm


THREAD_NO_PR = 0
THREAD_HAVE_PR_ROOMS = 1
THREAD_HAVE_PR_THREADS = 2


class RightsPlugin(ForumPlugin):
    def get_parent_rights(self, thread, user):
        no_parent_read = True
        no_parent_write = True
        parent_read = thread.parent.read_right(user) if (
            thread.parent_id) else no_parent_read
        parent_write = thread.parent.write_right(user) if (
            thread.parent_id) else no_parent_write
        parent_moderate = thread.parent.moderate_right(user) if (
            thread.parent_id) else user.is_superuser
        return parent_read, parent_write, parent_moderate

    def get_special_rights(self, thread, user):
        special_read = False
        special_write = False
        special_moderate = False
        if (not user.is_anonymous) and (
                thread.room or (
                    thread.access_type >
                    self.models.THREAD_ACCESS_TYPE_NOT_SET)):
            rights = self.models.ThreadAccessRight.objects.filter(
                thread=thread, user=user)
            for right in rights:
                if right.access_level & self.models.THREAD_ACCESS_READ:
                    special_read = True
                if right.access_level & self.models.THREAD_ACCESS_WRITE:
                    special_write = True
                if right.access_level & self.models.THREAD_ACCESS_MODERATE:
                    special_moderate = True
        return special_read, special_write, special_moderate

    def is_superuser_equal(self, thread, user, parent_moderate):
        # Not sure that
        # user.is_superuser if not user.is_anonymous else parent_moderate
        # more obvious
        # pylint: disable=consider-using-ternary
        return (
            (not user.is_anonymous) and user.is_superuser) or parent_moderate

    def limited_read_list(self, thread):
        persons = [
            right.user for right in
            self.models.ThreadAccessRight.objects.filter(thread=thread)]
        if thread.parent and thread.parent.limited_read:
            parent_list = thread.parent.limited_read_list
            persons = [person for person in persons if person in parent_list]
        return persons

    def get_rights(self, thread):
        user = thread.view_user
        author = (not user.is_anonymous) and (
            (user.id == thread.user_id) or user.is_superuser)
        (parent_read, parent_write, parent_moderate) = \
            self.get_parent_rights(thread, user)
        thread.limited_read = (
            thread.access_type == self.models.THREAD_ACCESS_TYPE_NO_READ)
        thread.limited_read_list = []
        if thread.limited_read:
            thread.limited_read_list = self.limited_read_list(thread)
        elif thread.parent:
            thread.limited_read = thread.parent.limited_read
            thread.limited_read_list = thread.parent.limited_read_list
        is_superuser_equal = self.is_superuser_equal(
            thread, user, parent_moderate)
        if is_superuser_equal:
            special_read, special_write, special_moderate = True, True, True
        else:
            special_read, special_write, special_moderate = \
                self.get_special_rights(thread, user)
        moderate_right = \
            parent_moderate or special_moderate or is_superuser_equal
        read_right = parent_read and (
            (thread.access_type < self.models.THREAD_ACCESS_TYPE_NO_READ)
            or special_read or moderate_right or author)
        if thread.access_type == self.models.THREAD_ACCESS_TYPE_NOT_SET:
            write_right = parent_write
        else:
            write_right = (
                thread.access_type < self.models.THREAD_ACCESS_TYPE_NO_WRITE)
        write_right = author or write_right or special_write or moderate_right
        view_right = read_right or author or moderate_right
        edit_right = author or moderate_right
        if thread.closed or user.is_anonymous:
            write_right = False
        if thread.deleted:
            read_right = False
            write_right = False
            view_right = author or moderate_right
            edit_right = moderate_right
        move_right = edit_right
        return (
            read_right, view_right, write_right, edit_right, move_right,
            moderate_right)

    def get_free_descendants(self, thread):
        query = Q(access_type__lt=self.models.THREAD_ACCESS_TYPE_NO_READ)
        if thread and thread.view_user and (
                not thread.view_user.is_anonymous):
            query = query | Q(user=thread.view_user)
        return self.models.Thread.objects.get_descendants(thread).filter(query)

    def get_readeable_protected_descendants(self, thread):
        user = thread.view_user
        if user.is_superuser:
            return self.models.Thread.objects.get_descendants(
                thread
            ).filter(
                access_type=self.models.THREAD_ACCESS_TYPE_NO_READ,
                deleted=False)
        if user.is_anonymous:
            return []
        rights = self.models.ThreadAccessRight.objects.filter(
            user=user, thread__tree_id=thread.tree_id,
            thread__lft__gt=thread.lft, thread__rght__lt=thread.rght,
            access_level__gte=self.models.THREAD_ACCESS_READ,
            thread__deleted=False)
        rights = rights.select_related('thread')
        return [right.thread for right in rights]

    def get_free_childs(self, thread):
        user = thread.view_user
        threads = self.models.Thread.objects.filter(
            access_type__lt=self.models.THREAD_ACCESS_TYPE_NO_READ,
            parent_id=int(thread.id))
        if user.is_anonymous:
            query = Q(access_type__lt=self.models.THREAD_ACCESS_TYPE_NO_READ)
        else:
            query = (Q(
                access_type__lt=self.models.THREAD_ACCESS_TYPE_NO_READ
            ) | Q(user=user))
        return threads.filter(query)

    def get_readeable_protected_childs(self, thread):
        user = thread.view_user
        if user.is_superuser or (thread.moderate_right(user)):
            return self.models.Thread.objects.filter(
                parent=thread,
                access_type=self.models.THREAD_ACCESS_TYPE_NO_READ)
        if user.is_anonymous:
            return []
        query = Q(
            thread__parent=thread,
            thread__access_type=self.models.THREAD_ACCESS_TYPE_NO_READ,
            access_level__gte=self.models.THREAD_ACCESS_READ, user=user)
        query = query & (Q(thread__deleted=False) | Q(thread__user=user))
        rights = self.models.ThreadAccessRight.objects.filter(query)
        rights = rights.select_related('thread')
        return [right.thread for right in rights]

    def get_moderators(self, thread):
        rights = self.models.ThreadAccessRight.objects.filter(
            thread_id=thread.id,
            access_level__gt=self.models.THREAD_ACCESS_MODERATE)
        rights = rights.select_related('user')
        return [right.user for right in rights]

    def get_accessed_users(self, thread):
        rights = self.models.ThreadAccessRight.objects.filter(
            thread_id=thread.id).select_related('user').distinct()
        return [right.user for right in rights]

    def comment_edit_right(self, comment):
        return (
            (comment.user == comment.view_user) or
            comment.parent.moderate_right(comment.view_user))

    def init_core(self):
        super(RightsPlugin, self).init_core()
        self.core['Comment_edit_right'] = self.comment_edit_right

        self.core['Thread_get_free_descendants'] = self.get_free_descendants
        self.core['Thread_get_moderators'] = self.get_moderators
        self.core['Thread_get_readeable_protected_descendants'] = \
            self.get_readeable_protected_descendants
        self.core['Thread_get_free_childs'] = self.get_free_childs
        self.core['Thread_get_readeable_protected_childs'] = \
            self.get_readeable_protected_childs
        self.core['Thread_get_readeable_protected'] = \
            self.get_readeable_protected_childs
        self.core['Thread_get_accessed_users'] = self.get_accessed_users
        self.core['Thread_get_rights'] = self.get_rights
        self.core['right_model'] = self.site.models.ThreadAccessRight
        self.core['right_form'] = ThreadAccessRightForm
