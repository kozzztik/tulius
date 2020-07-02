from django import dispatch
from django import http
from django import shortcuts
from django.core import exceptions
from django.utils.translation import ugettext_lazy as _

from tulius.forum import plugins


ERROR_VALIDATION = _('there were some errors during form validation')


class ThreadsCorePlugin(plugins.ForumPlugin):
    def get_parent_thread(self, user, thread_id, is_room=None):
        try:
            thread_id = int(thread_id)
        except:
            raise http.Http404()
        if is_room is None:
            parent_post = shortcuts.get_object_or_404(
                self.site.core.models.Thread,
                id=thread_id, plugin_id=self.site_id)
        else:
            parent_post = shortcuts.get_object_or_404(
                self.site.core.models.Thread,
                id=thread_id, plugin_id=self.site_id, room=is_room)
        if parent_post.check_deleted():
            raise http.Http404(str(_('Post was deleted')))
        if not parent_post.read_right(user):
            raise exceptions.PermissionDenied()
        return parent_post

    def room_descendants(self, user, room):
        if room.rght - room.lft <= 1:
            return [], []
        room_list = room.get_free_descendants.filter(room=True, deleted=False)
        room_list = [thread for thread in room_list]
        protected_threads = []
        if room.protected_threads:
            protected_threads = room.get_readeable_protected_descendants
            room_list += [
                thread for thread in protected_threads if thread.room]
        new_room_list = []
        while room_list:
            tested_room = room_list.pop(0)
            parent_id = tested_room.parent_id
            found_parent = (parent_id == room.id)
            if not found_parent:
                for tmp in room_list:
                    if tmp.id == parent_id:
                        found_parent = True
                        break
            if not found_parent:
                for tmp in new_room_list:
                    if tmp.id == parent_id:
                        found_parent = True
                        break
            if not found_parent:
                lft = tested_room.lft
                rght = tested_room.rght
                room_list = [
                    tmp for tmp in room_list if
                    not ((tmp.lft > lft) and (tmp.rght < rght))]
                new_room_list = [
                    tmp for tmp in new_room_list if
                    not ((tmp.lft > lft) and (tmp.rght < rght))]
            else:
                new_room_list += [tested_room]
        room_ids = [tmp.id for tmp in new_room_list]
        threads = room.get_free_descendants.filter(room=False, deleted=False)
        threads = [thread for thread in threads]
        if room.protected_threads:
            threads += [
                thread for thread in protected_threads if not thread.room]
        threads = [
            thread for thread in threads if
            (thread.parent_id == room.id) or (thread.parent_id in room_ids)]
        return new_room_list, threads

    def search_list(self, user, parent, **kwargs):
        queryset = self.models.Thread.objects.filter(
            plugin_id=self.site_id, deleted=False, parent=parent, **kwargs)
        thread_list = []
        for thread in queryset:
            thread.parent = parent
            if not thread.read_right(user):
                continue
            thread_list += [thread] + self.search_list(user, thread, **kwargs)
        return thread_list

    def expand_move_list(self, queryset, thread, user):
        thread_list = []
        for room in queryset:
            if (
                    not room.is_descendant_of(thread, include_self=True)) and \
                    room.write_right(user):
                thread_list += [room]
                if room.get_descendant_count():
                    subqueryset = room.get_children().filter(
                        room=True, deleted=False)
                    for subroom in subqueryset:
                        subroom.parent = room
                    thread_list += self.expand_move_list(
                        subqueryset, thread, user)
        return thread_list

    def move_list(self, thread, user):
        queryset = self.models.Thread.objects.filter(
            plugin_id=self.site_id, level=0, room=True, deleted=False)
        move_list = self.expand_move_list(queryset, thread, user)
        if user.is_superuser and thread.room:
            move_list = [None] + move_list
        return move_list

    def move_thread(self, thread, user, new_parent):
        if not thread.edit_right(user):
            raise http.Http404("no rights")
        if new_parent:
            if not new_parent.write_right(user):
                raise http.Http404("no rights")
        else:
            if not user.is_superuser:
                raise http.Http404("no rights")
        if new_parent not in self.move_list(thread, user):
            raise http.Http404("bad new parent")
        if new_parent and new_parent.is_descendant_of(
                thread, include_self=True):
            raise http.Http404("can`t move to a descendant")
        old_parent = thread.parent
        old_tree_id = thread.tree_id
        thread.parent = new_parent
        thread.save()
        if old_parent and ((not new_parent) or (
                old_parent.tree_id != new_parent.tree_id)):
            obj = self.models.Thread.objects.get(
                tree_id=old_parent.tree_id, parent=None)
            self.repair_thread_counters(obj, only_stats=True)
            obj.save()
        if new_parent:
            obj = self.models.Thread.objects.get(
                tree_id=new_parent.tree_id, parent=None)
            self.repair_thread_counters(obj, only_stats=True)
            obj.save()

    def repair_thread_counters(self, thread=None, only_stats=False):
        if not only_stats:
            if thread:
                self.models.Thread.objects.partial_rebuild(thread.tree_id)
            else:
                self.models.Thread.objects.rebuild()
        self._repair_thread_counters(thread)

    def _repair_thread_counters(self, thread=None):
        threads = self.models.Thread.objects.filter(
            parent=thread, deleted=False)
        for t in threads:
            if t.room:
                self._repair_thread_counters(t)
            self.thread_repair_counters.send(t)
            t.save()

    def init_core(self):
        self.thread_view_signal = dispatch.Signal(
            providing_args=["context", "user", "request"])

        self.thread_repair_counters = dispatch.Signal(providing_args=[])
        self.thread_on_create = dispatch.Signal(providing_args=['instance'])
        self.thread_on_update = dispatch.Signal(
            providing_args=["old_thread"])
        self.core['get_parent_thread'] = self.get_parent_thread
        self.core['room_descendants'] = self.room_descendants
        self.core['move_thread'] = self.move_thread
        self.core['thread_move_list'] = self.move_list
        self.core['Thread_rebuild'] = self.repair_thread_counters
        self.core['rebuild_tree'] = self.repair_thread_counters
        self.core['threads_search_list'] = self.search_list
        self.signals['thread_view'] = self.thread_view_signal
        self.signals['thread_repair_counters'] = self.thread_repair_counters
        self.signals['thread_on_create'] = self.thread_on_create
        self.signals['thread_on_update'] = self.thread_on_update
