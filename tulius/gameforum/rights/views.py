from django import dispatch
from django import urls

from tulius.forum.rights import views
from tulius.forum.threads import signals as thread_signals
from tulius.gameforum import consts
from tulius.gameforum import models
from tulius.gameforum.threads import views as threads_api


@dispatch.receiver(thread_signals.after_create)
def after_create_thread(instance, data, preview, view, **_kwargs):
    if (instance.plugin_id != consts.GAME_FORUM_SITE_ID) or preview:
        return
    for right in data['granted_rights']:
        models.GameThreadRight(
            thread=instance, role=view.rights.all_roles[right['user']['id']],
            access_level=right['access_level']).save()


class BaseGrantedRightsAPI(
        views.BaseGrantedRightsAPI, threads_api.BaseThreadAPI):
    rights_model = models.GameThreadRight

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
        obj = self.rights_model.objects.get_or_create(
            thread=self.obj, role_id=data['user']['id'],
            defaults={'access_level': data['access_level']}
        )[0]
        obj.access_level = obj.access_level | data['access_level']
        return obj


@dispatch.receiver(thread_signals.on_fix_counters)
def tmp_on_fix_plugin_filter(sender, thread, view, **kwargs):
    # TODO this func will be removed with plugin_id field cleanup
    # it will use signals "sender" field
    if thread.plugin_id != consts.GAME_FORUM_SITE_ID:
        return None
    return GrantedRightsAPI.on_fix_counters(sender, thread, view, **kwargs)


class GrantedRightsAPI(views.GrantedRightsAPI, BaseGrantedRightsAPI):
    pass


class GrantedRightAPI(views.GrantedRightAPI, BaseGrantedRightsAPI):
    pass
