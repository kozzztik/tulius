import datetime

from redis import client
from django import dispatch
from django.conf import settings
from django.contrib import auth
from django.core.cache import cache
from django.utils import html
from django.db import transaction

from tulius.forum import core
from tulius.forum.threads import models as thread_models
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


def thread_key(model, pk):
    return f'{model._meta.db_table}_{pk}_online'


class OnlineStatusAPI(core.BaseAPIView):
    thread_model = thread_models.Thread
    thread = None
    online_timeout = 3  # minutes

    def update_online_status(self, redis, timestamp, timeout):
        if self.user.is_anonymous:
            return
        threads = ['None']
        if self.thread:
            threads += self.thread.parents_ids + [self.thread.pk]
        keys = [thread_key(self.thread_model, key) for key in threads]
        pipe = redis.pipeline()
        for key in keys:
            pipe.zadd(key, {self.user.pk: timestamp})
            pipe.zremrangebyscore(
                key, min=float('-inf'), max=timestamp - timeout)
            pipe.expire(key, timeout)
        pipe.execute()
        set_user_status(self.user.id, self.thread.id if self.thread else None)

    def get_online_users_ids(self, do_update=True):
        redis = client.Redis(**settings.REDIS_CONNECTION)
        timestamp = datetime.datetime.now().timestamp()
        timeout = self.online_timeout * 60
        if do_update:
            self.update_online_status(redis, timestamp, timeout)
        return redis.zrangebyscore(
            thread_key(
                self.thread_model, self.thread.pk if self.thread else 'None'),
            min=timestamp - timeout,
            max=float('+inf')
        )

    def get_online_users(self, do_update=True):
        ids = self.get_online_users_ids(do_update=do_update)
        # some magic to preserve order
        users = auth.get_user_model().objects.filter(
            pk__in=ids)
        users = {u.pk: u for u in users}
        return [users.get(int(pk)) for pk in ids]

    @transaction.non_atomic_requests
    def get(self, request, *args, **kwargs):
        pk = kwargs['pk'] if 'pk' in kwargs else None
        if pk:
            self.thread = self.thread_model.objects.get(pk=pk)
        users = self.get_online_users()
        return {
            'users': [{
                'id': user.pk,
                'title': html.escape(str(user)),
                'url': user.get_absolute_url(),
            } for user in users]
        }
