from django.utils import timezone

from tulius.stories import models
from tulius.forum import online_status
from tulius.gameforum import views


class GameOnlineStatusPlugin(online_status.OnlineStatusPlugin):
    online_list_template = 'gameforum/snippets/online_roles.haml'

    def update_role_online_status(self, user, variation):
        if variation.game_id and (not user.is_anonymous):
            models.Role.objects.filter(
                variation=variation, user=user
            ).update(visit_time=timezone.now())

    def get_online_roles(self, user, thread, do_update=True):
        variation = thread.variation
        if do_update:
            self.update_role_online_status(user, variation)
        users = self.get_online_users(user, thread, do_update)
        roles = models.Role.objects.filter(
            variation=variation, show_in_online_character=True, user__in=users)
        strict_read = getattr(thread, 'strict_read', None)
        if strict_read is not None:
            roles = [role for role in roles if role in strict_read]
        return roles

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


class OnlineStatusAPI(online_status.OnlineStatusAPI, views.VariationMixin):
    def update_online_status(self):
        super(OnlineStatusAPI, self).update_online_status()
        if self.variation.game_id and (not self.user.is_anonymous):
            models.Role.objects.filter(
                variation=self.variation, user=self.user
            ).update(visit_time=timezone.now())

    def get_online_users(self, do_update=True):
        users = super(OnlineStatusAPI, self).get_online_users(
            do_update=do_update)
        roles = models.Role.objects.filter(
            variation=self.variation, show_in_online_character=True,
            user__in=users)
        return roles
