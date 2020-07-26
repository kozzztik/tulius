from django import dispatch

from tulius.forum.rights import views
from tulius.forum.threads import signals as thread_signals
from tulius.gameforum import models
from tulius.gameforum.threads import models as thread_models
from tulius.gameforum.threads import views as threads_api


@dispatch.receiver(thread_signals.after_create, sender=thread_models.Thread)
def after_create_thread(instance, data, preview, view, **_kwargs):
    if preview:
        return
    for right in data['granted_rights']:
        models.GameThreadRight(
            thread=instance, role=view.rights.all_roles[right['user']['id']],
            access_level=right['access_level']).save()


class BaseGrantedRightsAPI(
        views.BaseGrantedRightsAPI, threads_api.BaseThreadAPI):
    thread_model = thread_models.Thread
    rights_model = models.GameThreadRight

    def create_right(self, data):
        obj = self.rights_model.objects.get_or_create(
            thread=self.obj, role_id=data['user']['id'],
            defaults={'access_level': data['access_level']}
        )[0]
        obj.access_level = obj.access_level | data['access_level']
        return obj


class GrantedRightsAPI(views.GrantedRightsAPI, BaseGrantedRightsAPI):
    pass


thread_signals.on_fix_counters.connect(
    GrantedRightsAPI.on_fix_counters, sender=thread_models.Thread)


class GrantedRightAPI(views.GrantedRightAPI, BaseGrantedRightsAPI):
    pass
