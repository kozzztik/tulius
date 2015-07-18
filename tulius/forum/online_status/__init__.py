from django.utils.timezone import now
from datetime import timedelta
# TODO: fix this when module moved
from tulius.forum.plugins import ForumPlugin

class OnlineStatusPlugin(ForumPlugin):
    online_list_template = 'forum/snippets/online_users.haml'
    
    def update_online_status(self, user, thread):
        if (not user.is_anonymous()) and thread:
            online_mark = self.site.models.OnlineUser.objects.get_or_create(user=user, thread=thread)[0]
            online_mark.visit_time = now()
            online_mark.save()
    
    def get_online_users(self, user, thread, do_update=True):
        if do_update:
            self.update_online_status(user, thread)
        users = self.site.models.OnlineUser.objects.select_related('user').filter(visit_time__gte=now() - timedelta(minutes=3), 
                                                                 thread__tree_id=thread.tree_id, thread__lft__gte=thread.lft, 
                                                                 thread__rght__lte=thread.rght)
        users_list = {}
        for user in users:
            users_list[user.user.id] = user.user
        return users_list.values()
    
    def get_all_online_users(self):
        users = self.site.models.OnlineUser.objects.select_related('user').filter(visit_time__gte=now() - timedelta(minutes=3), 
                                                                 thread__plugin_id=self.site_id)
        users_list = {}
        for user in users:
            users_list[user.user.id] = user.user
        return users_list.values()
    
    def thread_view(self, sender, **kwargs):
        context = kwargs['context']
        if sender:
            user = kwargs["user"]
            context['online_users'] =  self.get_online_users(user, sender)
        else:
            context['online_users'] =  self.get_all_online_users()
            
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
        self.site.signals.thread_view.connect(self.thread_view)
        self.site.signals.read_comments.connect(self.comments_page)