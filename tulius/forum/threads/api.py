from django import http
from django import shortcuts
from django import urls
from django.core import exceptions
from django.core.cache import cache
from django.utils import html
from django.db.models import query_utils

from tulius.forum import site
from tulius.forum import plugins
from tulius.forum import const
from tulius.forum import models
from tulius.forum import signals
from tulius.forum import rights as forum_rights
from tulius.forum import online_status as online_status_plugin
from tulius.forum.readmarks import plugin as readmarks
from djfw.wysibb.templatetags import bbcodes


def user_to_json(user, detailed=False):
    data = {
        'id': user.id,
        'title': html.escape(str(user)),  # TODO
        'url': user.get_absolute_url(),
    }
    if detailed:
        if user.show_online_status:
            online_status = online_status_plugin.get_user_status(user.id)
        else:
            online_status = False
        data.update({
            'sex': user.sex,
            'avatar': user.avatar.url if user.avatar else '',
            'full_stars': user.full_stars(),
            'rank': html.escape(user.rank),
            'stories_author': user.stories_author(),  # TODO optimize that!
            'signature': bbcodes.bbcode(user.signature),
            'online_status': bool(online_status)
        })
    return data


class BaseThreadView(plugins.BaseAPIView):
    obj = None
    rights = None
    plugin_id = None

    def get_context_data(self, **kwargs):
        context = super(BaseThreadView, self).get_context_data(**kwargs)
        if self.obj is None:
            self.get_parent_thread(**kwargs)
        context['thread'] = self.obj
        return context

    def _get_rights_checker(self, thread, parent_rights=None):
        return forum_rights.default.DefaultRightsChecker(
            thread, self.user, parent_rights=parent_rights)

    def get_parent_thread(self, **kwargs):
        thread_id = kwargs['pk'] if 'pk' in kwargs else None
        try:
            thread_id = int(thread_id)
        except:
            raise http.Http404()
        self.obj = shortcuts.get_object_or_404(
            models.Thread, id=thread_id, plugin_id=self.plugin_id)
        # TODO delete all sub threads and rooms on room delete so it will be
        # TODO not needed to do parent check here
        if self.obj.check_deleted():
            raise http.Http404('Post was deleted')
        self.rights = self._get_rights_checker(self.obj).get_rights()
        if not self.rights.read:
            raise exceptions.PermissionDenied()

    def _thread_list_apply_rights(self, parent_rights, thread_list):
        for thread in thread_list:
            thread.rights_checker = self._get_rights_checker(
                thread, parent_rights=parent_rights)
            thread.rights = thread.rights_checker.get_rights()
        return [thread for thread in thread_list if thread.rights.read]

    @staticmethod
    def room_descendants(room):
        if room.rght - room.lft <= 1:
            return [], []
        readable = room.rights_checker.get_readable_descendants()
        room_list = [thread for thread in readable if thread.room]
        threads = [thread for thread in readable if not thread.room]
        new_room_list = []
        # TODO remove: looks like all this magic is needed just for case
        # TODO of filtering children of deleted rooms
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
        threads = [
            thread for thread in threads if
            (thread.parent_id == room.id) or (thread.parent_id in room_ids)]
        return new_room_list, threads

    def prepare_room_list(self, parent_rights, rooms):
        rooms = self._thread_list_apply_rights(parent_rights, rooms)
        for room in rooms:
            threads = self.room_descendants(room)[1]
            threads = self._thread_list_apply_rights(room.rights, threads)
            room.threads_count = len(threads)
            room.moderators, room.accessed_users = room.rights_checker\
                .get_moderators_and_accessed_users()
            signals.thread_prepare_room.send(
                self, room=room, threads=threads)
        return rooms

    def get_subthreads(self, is_room=False):
        threads = models.Thread.objects.filter(
            parent=self.obj, room=is_room).exclude(deleted=True)
        if not self.obj:
            threads = threads.filter(plugin_id=self.plugin_id)
        if is_room:
            return self.prepare_room_list(self.rights, threads)
        threads = threads.order_by('-last_comment_id')
        threads = self._thread_list_apply_rights(self.rights, threads)

        for thread in threads:
            thread.moderators = []
            thread.accessed_users = None
            if thread.access_type == models.THREAD_ACCESS_TYPE_NO_READ:
                thread.accessed_users = thread.rights_checker\
                    .get_moderators_and_accessed_users()[1]
        signals.thread_prepare_threads.send(self, threads=threads)
        return threads

    @staticmethod
    def thread_url(thread):
        return urls.reverse(
            'forum:room' if thread.room else 'forum:thread',
            kwargs={'parent_id': thread.id})

    def room_to_json(self, thread):
        return {
            'id': thread.pk,
            'title': html.escape(thread.title),
            'body': bbcodes.bbcode(thread.body),
            'room': thread.room,
            'deleted': thread.deleted,
            'important': thread.important,
            'closed': thread.closed,
            'user': user_to_json(thread.user),
            'moderators': [user_to_json(user) for user in thread.moderators],
            'accessed_users': None if thread.accessed_users is None else [
                user_to_json(user) for user in thread.accessed_users
            ],
            'threads_count': thread.threads_count if thread.room else None,
            'comments_count': thread.comments_count,
            'pages_count': thread.pages_count,
            'url': self.thread_url(thread),
            'last_comment': {
                'url': thread.last_comment.get_absolute_url,
                'user': user_to_json(thread.last_comment.user),
                'create_time': thread.last_comment.create_time,
            } if thread.last_comment else None,
            'unreaded':
                thread.unreaded.get_absolute_url if thread.unreaded else None,
        }


class ThreadView(BaseThreadView):
    def obj_to_json(self):
        return {
            'id': self.obj.pk,
            'tree_id': self.obj.tree_id,
            'title': self.obj.title,
            'body': self.obj.body,
            'room': self.obj.room,
            'deleted': self.obj.deleted,
            'url': self.thread_url(self.obj),
            'parents': [{
                'id': parent.id,
                'title': parent.title,
                'url': self.thread_url(parent),
            } for parent in self.obj.get_ancestors()],
            'rooms': [self.room_to_json(t) for t in self.get_subthreads(True)],
            'threads': [
                self.room_to_json(t) for t in self.get_subthreads(False)],
            'rights': self.rights.to_json(),
            'first_comment_id': self.obj.first_comment_id,
        }

    def get_context_data(self, **kwargs):
        super(ThreadView, self).get_context_data(**kwargs)
        # cache rights for async app
        cache.set(
            const.USER_THREAD_RIGHTS.format(
                user_id=self.user.id, thread_id=self.obj.id),
            'r', const.USER_THREAD_RIGHTS_PERIOD * 60
        )
        response = self.obj_to_json()
        signals.thread_view.send(self, response=response)
        return response

    def delete(self, request, *args, **kwargs):
        self.get_parent_thread(**kwargs)
        (success, error_text, _, text) = site.site.core.delete_thread(
            request.user, self.obj.id, request.GET['comment'])
        return {
            'result': success,
            'error_text': str(error_text),
            'text': str(text)
        }


class IndexView(BaseThreadView):
    def get_index(self, level):
        children = list(self.get_free_index(level)) + \
            list(self.get_readable_protected_index(level))
        children = [thread for thread in children if thread.room]
        return sorted(children, key=lambda x: x.id)

    def get_readable_protected_index(self, level):
        if self.user.is_superuser:
            return models.Thread.objects.filter(
                access_type=models.THREAD_ACCESS_TYPE_NO_READ,
                plugin_id=self.plugin_id, level=level, deleted=False)
        if self.user.is_anonymous:
            return []
        query = query_utils.Q(
            thread__level=level,
            thread__access_type=models.THREAD_ACCESS_TYPE_NO_READ,
            thread__plugin_id=self.plugin_id,
            access_level__gte=models.THREAD_ACCESS_READ,
            user=self.user, thread__deleted=False)
        rights = models.ThreadAccessRight.objects.filter(query)
        rights = rights.select_related('thread')
        return [right.thread for right in rights]

    def get_free_index(self, level):
        threads = models.Thread.objects.filter(
            access_type__lt=models.THREAD_ACCESS_TYPE_NO_READ,
            plugin_id=self.plugin_id, level=level, deleted=False)
        if self.user.is_anonymous:
            return threads
        return threads.filter(query_utils.Q(
            access_type__lt=models.THREAD_ACCESS_TYPE_NO_READ
        ) | query_utils.Q(user=self.user))  # TODO: move it to protected #97

    def get_context_data(self, **kwargs):
        all_rooms = [thread for thread in self.get_index(1)]
        groups = self.get_index(0)
        self.rights = self._get_rights_checker(None).get_rights_for_root()
        for group in groups:
            group.rooms = [
                thread for thread in all_rooms if thread.parent_id == group.id]
            for thread in group.rooms:
                thread.parent = group
            group.rooms = self.prepare_room_list(self.rights, group.rooms)
            # TODO refactor unread url, move it to readmarks
        return {
            'groups': [{
                'id': group.id,
                'title': group.title,
                'rooms': [self.room_to_json(thread) for thread in group.rooms],
                'url': group.get_absolute_url,
                'unreaded_url': readmarks.room_group_unreaded_url(group.rooms),
            } for group in groups]
        }
