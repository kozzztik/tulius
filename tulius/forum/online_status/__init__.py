from datetime import timedelta

from django.core.cache import cache
from django.utils.timezone import now

from tulius.forum import site
from tulius.forum import plugins
from tulius.forum import models
from tulius.forum import const


def set_user_status(user_id, thread_id):
    cache.set(
        const.USER_ONLINE_CACHE_KEY.format(user_id),
        thread_id or True, const.USER_ONLINE_PERIOD * 60)


def get_user_status(user_id):
    return cache.get(const.USER_ONLINE_CACHE_KEY.format(user_id), False)


class OnlineStatusPlugin(plugins.ForumPlugin):
    online_list_template = 'forum/snippets/online_users.haml'

    def update_online_status(self, user, thread):
        if (not user.is_anonymous) and thread:
            online_mark = self.site.models.OnlineUser.objects.get_or_create(
                user=user, thread=thread)[0]
            online_mark.visit_time = now()
            online_mark.save()
            set_user_status(user.id, thread.id)

    def get_online_users(self, user, thread, do_update=True):
        if do_update:
            self.update_online_status(user, thread)
        users = self.site.models.OnlineUser.objects.select_related(
            'user'
        ).filter(
            visit_time__gte=now() - timedelta(minutes=3),
            thread__tree_id=thread.tree_id, thread__lft__gte=thread.lft,
            thread__rght__lte=thread.rght)
        users_list = {u.user.id: u.user for u in users}
        return users_list.values()

    def get_all_online_users(self):
        users = models.OnlineUser.objects.select_related(
            'user'
        ).filter(
            visit_time__gte=now() - timedelta(minutes=3),
            thread__plugin_id=self.site_id)
        users_list = {}
        for user in users:
            users_list[user.user.id] = user.user
        return users_list.values()

    def comments_page(self, sender, **kwargs):
        user = kwargs["user"]
        comments = kwargs["comments"]
        online_users = self.get_online_users(user, sender)
        all_online_users = self.get_all_online_users()
        for comment in comments:
            comment.online = comment.user in all_online_users
            comment.online_here = comment.user in online_users

    def init_core(self):
        self.core['update_online_status'] = self.update_online_status
        self.core['get_online_users'] = self.get_online_users
        self.core['get_all_online_users'] = self.get_all_online_users
        self.templates['online_users'] = self.online_list_template
        self.site.signals.read_comments.connect(self.comments_page)


class OnlineStatusAPI(plugins.BaseAPIView):
    def get(self, request, *args, **kwargs):
        pk = kwargs['pk'] if 'pk' in kwargs else None
        if pk:
            thread = models.Thread.objects.get(pk=pk)
            users = site.site.core.get_online_users(self.user, thread)
        else:
            users = site.site.core.get_all_online_users()
        return {
            'users': [{
                'id': user.pk,
                'title': str(user),
                'url': user.get_absolute_url(),
            } for user in users]
        }
