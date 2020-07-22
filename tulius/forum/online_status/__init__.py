from datetime import timedelta

from django.core.cache import cache
from django.utils.timezone import now
from django.utils import html

from tulius.forum import core
from tulius.forum import models
from tulius.forum import const


def set_user_status(user_id, thread_id):
    cache.set(
        const.USER_ONLINE_CACHE_KEY.format(user_id),
        thread_id or True, const.USER_ONLINE_PERIOD * 60)


def get_user_status(user_id):
    return cache.get(const.USER_ONLINE_CACHE_KEY.format(user_id), False)


class OnlineStatusAPI(core.BaseAPIView):
    thread = None
    plugin_id = None
    online_timeout = 3  # minutes

    def update_online_status(self):
        if (not self.user.is_anonymous) and self.thread:
            online_mark = models.OnlineUser.objects.get_or_create(
                user=self.user, thread=self.thread)[0]
            online_mark.visit_time = now()
            online_mark.save()
            set_user_status(self.user.id, self.thread.id)

    def get_online_users(self, do_update=True):
        if do_update:
            self.update_online_status()
        users = models.OnlineUser.objects.select_related(
            'user'
        ).filter(
            visit_time__gte=now() - timedelta(minutes=self.online_timeout),
            thread__tree_id=self.thread.tree_id,
            thread__lft__gte=self.thread.lft,
            thread__rght__lte=self.thread.rght)
        users_list = {u.user.id: u.user for u in users}
        return users_list.values()

    def get_all_online_users(self):
        users = models.OnlineUser.objects.select_related(
            'user'
        ).filter(
            visit_time__gte=now() - timedelta(minutes=self.online_timeout),
            thread__plugin_id=self.plugin_id)
        users_list = {}
        for user in users:
            users_list[user.user.id] = user.user
        return users_list.values()

    def get(self, request, *args, **kwargs):
        pk = kwargs['pk'] if 'pk' in kwargs else None
        if pk:
            self.thread = models.Thread.objects.get(pk=pk)
            users = self.get_online_users()
        else:
            users = self.get_all_online_users()
        return {
            'users': [{
                'id': user.pk,
                'title': html.escape(str(user)),
                'url': user.get_absolute_url(),
            } for user in users]
        }
