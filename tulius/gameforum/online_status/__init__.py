from django.utils import timezone

from tulius.stories import models
from tulius.forum import online_status
from tulius.gameforum import base


class OnlineStatusAPI(online_status.OnlineStatusAPI, base.VariationMixin):
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
