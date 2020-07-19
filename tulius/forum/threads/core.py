from django import dispatch
from django.utils.translation import ugettext_lazy as _

from tulius.forum import plugins


ERROR_VALIDATION = _('there were some errors during form validation')


class ThreadsCorePlugin(plugins.ForumPlugin):
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
        self.thread_repair_counters = dispatch.Signal(providing_args=[])
        self.thread_on_create = dispatch.Signal(providing_args=['instance'])
        self.core['room_descendants'] = self.room_descendants
        self.core['Thread_rebuild'] = self.repair_thread_counters
        self.core['rebuild_tree'] = self.repair_thread_counters
        self.signals['thread_repair_counters'] = self.thread_repair_counters
        self.signals['thread_on_create'] = self.thread_on_create
