from django.utils.timezone import now
from datetime import timedelta
# TODO: fix this when module moved
from tulius.forum.plugins import ForumPlugin
from tulius.stories.models import Role
from tulius.forum.online_status import OnlineStatusPlugin


class GameOnlineStatusPlugin(OnlineStatusPlugin):
    online_list_template = 'gameforum/snippets/online_roles.haml'
    
    def update_role_online_status(self, user, variation):
        if variation.game_id and (not user.is_anonymous()):
            Role.objects.filter(
                variation=variation, user=user).update(visit_time=now())
    
    def get_online_roles(self, user, thread, do_update=True):
        variation = thread.variation
        if do_update:
            self.update_role_online_status(user, variation)
        users = self.get_online_users(user, thread, do_update)
        roles = Role.objects.filter(
            variation=variation, show_in_online_character=True, user__in=users)
        strict_read = getattr(thread, 'strict_read', None)
        if strict_read is not None:
            roles = [role for role in roles if role in strict_read]
        return roles

    def thread_view(self, sender, **kwargs):
        context = kwargs['context']
        user = kwargs["user"]
        context['online_roles'] = self.get_online_roles(user, sender)
            
    def comments_page(self, sender, **kwargs):
        user = kwargs["user"] 
        comments = kwargs["comments"]
        online_roles = self.get_online_roles(user, sender)
        role_ids = [role.id for role in online_roles]
        sender.online_roles = online_roles
        for role in sender.all_roles:
            if role.id in role_ids:
                role.is_online = True
        for comment in comments:
            role_id = comment.data1
            comment.online_here = role_id and (role_id in role_ids)
            
    def init_core(self):
        super(GameOnlineStatusPlugin, self).init_core()
        self.core['update_role_online_status'] = self.update_role_online_status
        self.core['get_online_roles'] = self.get_online_roles
