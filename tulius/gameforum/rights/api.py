from django import dispatch
from django import urls

from tulius.forum import signals
from tulius.forum.rights import api
from tulius.gameforum import consts
from tulius.gameforum import models
from tulius.gameforum.threads import api as threads_api


@dispatch.receiver(signals.after_create_thread)
def after_create_thread(sender, thread, data, **kwargs):
    if sender.plugin_id != consts.GAME_FORUM_SITE_ID:
        return
    for right in data['granted_rights']:
        models.GameThreadRight(
            thread=thread, role=sender.rights.all_roles[right['user']['id']],
            access_level=right['access_level']).save()


class BaseGrantedRightsAPI(api.BaseGrantedRightsAPI, threads_api.BaseThreadAPI):
    model = models.GameThreadRight

    def right_to_json(self, right):
        return {
            'id': right.pk,
            'user': {
                'id': right.role.pk,
                'title': right.role.name,
            },
            'access_level': right.access_level,
            'url': urls.reverse(
                'game_forum_api:thread_right',
                kwargs={
                    'pk': self.obj.id,
                    'right_id': right.pk,
                    'variation_id': self.variation.pk
                }),
        }

    def create_right(self, data):
        obj = self.model.objects.get_or_create(
            thread=self.obj, role_id=data['user']['id'],
            defaults={'access_level': data['access_level']}
        )[0]
        obj.access_level = obj.access_level | data['access_level']
        return obj


class GrantedRightsAPI(api.GrantedRightsAPI, BaseGrantedRightsAPI):
    pass


class GrantedRightAPI(api.GrantedRightAPI, BaseGrantedRightsAPI):
    pass
