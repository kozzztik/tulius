from django import dispatch

from tulius.forum.rights import views
from tulius.forum.threads import signals as thread_signals
from tulius.gameforum import models
from tulius.gameforum.threads import models as thread_models
from tulius.gameforum.threads import views as threads_api
from tulius.gameforum.rights import mutations
from tulius.games import signals as game_signals
from tulius.stories import models as stories_models


@dispatch.receiver(thread_signals.before_create, sender=thread_models.Thread)
def before_create_thread(instance, data, preview, view, **_kwargs):
    if not preview:
        mutations.UpdateRightsOnThreadCreate(
            instance, data, variation=view.variation).apply()


@dispatch.receiver(thread_signals.after_create, sender=thread_models.Thread)
def after_create_thread(instance, data, preview, view, **_kwargs):
    if not preview:
        mutations.UpdateRightsOnThreadCreate(
            instance, data, variation=view.variation).save_exceptions()


@dispatch.receiver(game_signals.game_status_changed)
def game_status_changed(sender, **_kwargs):
    variation = sender.variation
    if variation.thread:
        mutations.UpdateRights(variation.thread, variation).apply()


class BaseGrantedRightsAPI(
        views.BaseGrantedRightsAPI, threads_api.BaseThreadAPI):
    rights_model = models.GameThreadRight

    def get_mutation(self, thread):
        return mutations.UpdateRights(thread, self.variation)

    def create_right(self, data):
        obj = self.rights_model.objects.get_or_create(
            thread=self.obj, role_id=data['user']['id'],
            defaults={'access_level': data['access_level']}
        )[0]
        obj.access_level = obj.access_level | data['access_level']
        return obj


class GrantedRightsAPI(views.GrantedRightsAPI, BaseGrantedRightsAPI):
    @classmethod
    def on_fix_counters(cls, sender, thread, view, **kwargs):
        variation = stories_models.Variation.objects.get(pk=thread.variation_id)
        mutations.UpdateRights(thread, variation).apply()


thread_signals.on_fix_counters.connect(
    GrantedRightsAPI.on_fix_counters, sender=thread_models.Thread)


class GrantedRightAPI(views.GrantedRightAPI, BaseGrantedRightsAPI):
    pass


def init():
    pass
