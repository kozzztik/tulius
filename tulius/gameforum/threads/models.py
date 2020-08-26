from django import urls
from django.db import models
from django.contrib.auth import get_user_model

from tulius.forum.threads import models as thread_models


User = get_user_model()


class Thread(thread_models.AbstractThread):
    role_id = models.IntegerField(blank=True, null=True)
    edit_role_id = models.IntegerField(blank=True, null=True)
    variation_id = models.IntegerField(blank=False, null=False)

    def get_absolute_url(self):
        return urls.reverse(
            'game_forum_api:thread',
            kwargs={
                'variation_id': self.variation_id, 'pk': self.pk})

    @property
    def moderators(self):
        return [
            int(pk) for pk, right in self.data['rights']['roles'].items()
            if right & thread_models.ACCESS_MODERATE]

    @property
    def accessed_users(self):
        if self.default_rights != thread_models.NO_ACCESS:
            return None
        return [
            int(pk) for pk, right in self.data['rights']['roles'].items()
            if right & thread_models.ACCESS_READ]

    def rights_to_json(self, user):
        return {
            'write': self.write_right(user),
            'moderate': self.moderate_right(user),
            'edit': self.edit_right(user),
            'move': self.moderate_right(user),
        }
