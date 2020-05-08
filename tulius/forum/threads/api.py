from tulius.forum import site
from tulius.forum import plugins


def user_to_json(user):
    return {
        'id': user.id,
        'title': str(user),  # TODO
        'url': user.get_absolute_url(),
    }


def room_to_json(thread):
    return {
        'id': thread.pk,
        'title': thread.title,
        'body': thread.body,
        'room': thread.room,
        'deleted': thread.deleted,
        'moderators': [user_to_json(user) for user in thread.moderators],
        'accessed_users': None if thread.accessed_users is None else [
            user_to_json(user) for user in thread.accessed_users
        ],
        'threads_count': thread.threads_count,
        'comments_count': thread.comments_count,
        'url': thread.get_absolute_url,
        'last_comment': {
            'url': thread.last_comment.get_absolute_url,
            'user': user_to_json(thread.last_comment.user),
            'create_time': thread.last_comment.create_time.strftime(
                "%d.%m.%Y, %H:%M"),
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
            site.site.signals.thread_prepare_room_group.send(
                group, user=self.request.user)
        site.site.signals.thread_view.send(
            None, context=context, user=self.request.user,
            request=self.request)
        # TODO online users
        # TODO deleted class in room list?
        # TODO refactor signals
        # TODO refactor this class
        return {
            'is_superuser': self.user.is_superuser,
            'is_anonymous' : self.user.is_anonymous,
            'groups': [{
                'id': group.id,
                'title': group.title,
                'rooms': [room_to_json(thread) for thread in group.rooms],
                'url': group.get_absolute_url,
                'unreaded': {
                    'url': group.unreaded.get_absolute_url,
                } if group.unreaded else None,
            } for group in groups]
        }
