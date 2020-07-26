from datetime import timedelta

from django import dispatch
from django.core.cache import cache
from django.utils.timezone import now
from django.utils import html

from tulius.forum import core
from tulius.forum.threads import models as thread_models
from tulius.forum.other import models
from tulius.forum import const
from tulius import signals


@dispatch.receiver(signals.user_to_json)
def user_to_json(instance, response, detailed, **_kwargs):
    if detailed:
        if instance.show_online_status:
            online_status = get_user_status(instance.id)
        else:
            online_status = False
        response['online_status'] = bool(online_status)


def set_user_status(user_id, thread_id):
    cache.set(
        const.USER_ONLINE_CACHE_KEY.format(user_id),
        thread_id or True, const.USER_ONLINE_PERIOD * 60)


def get_user_status(user_id):
    return cache.get(const.USER_ONLINE_CACHE_KEY.format(user_id), False)


class OnlineStatusAPI(core.BaseAPIView):
    online_user_model = models.OnlineUser
    thread_model = thread_models.Thread
    thread = None
    online_timeout = 3  # minutes

    def update_online_status(self):
        if (not self.user.is_anonymous) and self.thread:
            online_mark = self.online_user_model.objects.get_or_create(
                user=self.user, thread=self.thread)[0]
            online_mark.visit_time = now()
            online_mark.save()
            set_user_status(self.user.id, self.thread.id)

    def get_online_users(self, do_update=True):
        if do_update:
            self.update_online_status()
        users = self.online_user_model.objects.select_related(
            'user'
        ).filter(
            visit_time__gte=now() - timedelta(minutes=self.online_timeout),
            thread__tree_id=self.thread.tree_id,
            thread__lft__gte=self.thread.lft,
            thread__rght__lte=self.thread.rght)
        users_list = {u.user.id: u.user for u in users}
        return users_list.values()

    def get_all_online_users(self):
        users = self.online_user_model.objects.select_related(
            'user'
        ).filter(
            visit_time__gte=now() - timedelta(minutes=self.online_timeout))
        users_list = {}
        for user in users:
            users_list[user.user.id] = user.user
        return users_list.values()

    def get(self, request, *args, **kwargs):
        pk = kwargs['pk'] if 'pk' in kwargs else None
        if pk:
            self.thread = self.thread_model.objects.get(pk=pk)
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
