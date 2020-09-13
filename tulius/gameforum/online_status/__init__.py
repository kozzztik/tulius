import datetime

from django.utils import timezone

from tulius.stories import models
from tulius.forum import online_status
from tulius.gameforum import base
from tulius.gameforum.threads import models as thread_models


class OnlineStatusAPI(online_status.OnlineStatusAPI, base.VariationMixin):
    thread_model = thread_models.Thread

    def update_online_status(self, redis, timestamp, timeout):
        super(OnlineStatusAPI, self).update_online_status(
            redis, timestamp, timeout)
        if self.variation.game_id and (not self.user.is_anonymous):
            models.Role.objects.filter(
                variation=self.variation, user=self.user
            ).update(visit_time=timezone.now())

    def get_online_users(self, do_update=True):
        ids = self.get_online_users_ids(do_update=do_update)
        roles = models.Role.objects.filter(
            variation=self.variation, show_in_online_character=True,
            user_id__in=ids)
        return roles


def get_online_roles(variation):
    v = timezone.now() - datetime.timedelta(
        minutes=OnlineStatusAPI.online_timeout)
    return models.Role.objects.filter(
        variation=variation, show_in_online_character=True,
        visit_time__gte=v)
