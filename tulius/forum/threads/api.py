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


class BaseThreadView(plugins.BaseAPIView):
    obj = None
    view_mode = True
    is_room = False

    def get_context_data(self, **kwargs):
        context = super(BaseThreadView, self).get_context_data(**kwargs)
        self.get_parent_thread(**kwargs)
        context['thread'] = self.obj
        if self.obj and self.view_mode:
            site.site.signals.thread_view.send(
                self.obj, context=context,
                user=self.request.user, request=self.request)
        return context

    def get_parent_thread(self, **kwargs):
        core = site.site.core
        parent_id = kwargs['pk'] if 'pk' in kwargs else None
        self.obj = core.get_parent_thread(
            self.user, parent_id, self.is_room) if parent_id else None


class ThreadView(BaseThreadView):
    is_room = True  # TODO remove

    def get_context_data(self, **kwargs):
        super(ThreadView, self).get_context_data(**kwargs)
        # todo online users
        # todo actions & search
        # todo empty page
        return {
            'id': self.obj.pk,
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
        }
