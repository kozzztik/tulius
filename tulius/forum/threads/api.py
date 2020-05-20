from django.core.cache import cache
from django.utils import html

from tulius.forum import site
from tulius.forum import plugins
from tulius.forum import const
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


def room_to_json(thread):
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
        'url': thread.get_absolute_url,
        'last_comment': {
            'url': thread.last_comment.get_absolute_url,
            'user': user_to_json(thread.last_comment.user),
            'create_time': thread.last_comment.create_time,
        } if thread.last_comment else None,
        'unreaded':
            thread.unreaded.get_absolute_url if thread.unreaded else None,
    }


class IndexView(plugins.BaseAPIView):
    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        core = site.site.core
        all_rooms = [thread for thread in core.get_index(self.user, 1)]
        groups = core.get_index(self.user, 0)
        context['groups'] = groups
        for group in groups:
            group.rooms = [
                thread for thread in all_rooms if thread.parent_id == group.id]
            for thread in group.rooms:
                thread.parent = group
            group.rooms = core.prepare_room_list(
                self.user, None, group.rooms)
        # TODO refactor this class
        return {
            'is_superuser': self.user.is_superuser,
            'is_anonymous' : self.user.is_anonymous,
            'groups': [{
                'id': group.id,
                'title': group.title,
                'rooms': [room_to_json(thread) for thread in group.rooms],
                'url': group.get_absolute_url,
                'unreaded_url': readmarks.room_group_unreaded_url(group.rooms),
            } for group in groups]
        }


class BaseThreadView(plugins.BaseAPIView):
    obj = None

    def get_context_data(self, **kwargs):
        context = super(BaseThreadView, self).get_context_data(**kwargs)
        if self.obj is None:
            self.get_parent_thread(**kwargs)
        context['thread'] = self.obj
        return context

    def get_parent_thread(self, **kwargs):
        core = site.site.core
        parent_id = kwargs['pk'] if 'pk' in kwargs else None
        self.obj = core.get_parent_thread(
            self.user, parent_id) if parent_id else None


class ThreadView(BaseThreadView):
    def get_context_data(self, **kwargs):
        super(ThreadView, self).get_context_data(**kwargs)
        # cache rights for async app
        cache.set(
            const.USER_THREAD_RIGHTS.format(
                user_id=self.user.id, thread_id=self.obj.id),
            'r', const.USER_THREAD_RIGHTS_PERIOD * 60
        )
        return {
            'id': self.obj.pk,
            'tree_id': self.obj.tree_id,
            'title': self.obj.title,
            'body': self.obj.body,
            'room': self.obj.room,
            'deleted': self.obj.deleted,
            'url': self.obj.get_absolute_url,
            'parents': [{
                'id': parent.id,
                'title': parent.title,
                'url': parent.get_absolute_url,
            } for parent in self.obj.get_ancestors()],
            'rooms': [
                room_to_json(room) for room in
                site.site.core.get_subthreads(self.user, self.obj, True)],
            'threads': [
                room_to_json(thread) for thread in
                site.site.core.get_subthreads(self.user, self.obj, False)],
            'rights': {
                'write': self.obj.write_right(),
                'moderate': self.obj.moderate_right(),
                'edit': self.obj.edit_right(),
                'move': self.obj.move_right(),
            },
            'first_comment_id': self.obj.first_comment_id,
        }

    def delete(self, request, *args, **kwargs):
        self.get_parent_thread(**kwargs)
        (success, error_text, _, text) = site.site.core.delete_thread(
            request.user, self.obj.id, request.GET['comment'])
        return {
            'result': success,
            'error_text': str(error_text),
            'text': str(text)
        }
