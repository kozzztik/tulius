from django import dispatch
from django.db import models as dj_models

from tulius.forum.rights import views
from tulius.forum.threads import signals as thread_signals
from tulius.gameforum import models
from tulius.gameforum.threads import models as thread_models
from tulius.gameforum.threads import views as threads_api
from tulius.gameforum.rights import mutations
from tulius.games import signals as game_signals
from tulius.games import models as game_models
from tulius.stories import models as stories_models


@dispatch.receiver(thread_signals.after_create, sender=thread_models.Thread)
def after_create_thread(instance, data, preview, **_kwargs):
    if not preview:
        mutations.UpdateRightsOnThreadCreate(
            instance, data=data).save_exceptions()


@dispatch.receiver(game_signals.game_status_changed)
def game_status_changed(sender, **_kwargs):
    variation = sender.variation
    if variation.thread:
        # to use actual variation info on thread
        variation.thread.variation = variation
        mutations.UpdateRights(variation.thread).apply()


@dispatch.receiver(dj_models.signals.post_delete, sender=game_models.GameAdmin)
@dispatch.receiver(dj_models.signals.post_save, sender=game_models.GameAdmin)
@dispatch.receiver(dj_models.signals.post_delete, sender=game_models.GameGuest)
@dispatch.receiver(dj_models.signals.post_save, sender=game_models.GameGuest)
def on_game_models_updates(instance, **_kwargs):
    variation = instance.game.variation
    if variation.thread:
        mutations.UpdateRights(variation.thread).apply()


@dispatch.receiver(
    dj_models.signals.post_delete, sender=stories_models.StoryAdmin)
@dispatch.receiver(
    dj_models.signals.post_save, sender=stories_models.StoryAdmin)
def on_stories_models_updates(instance, **_kwargs):
    for variation in instance.story.variations.all():
        if variation.thread:
            mutations.UpdateRights(variation.thread).apply()


@dispatch.receiver(dj_models.signals.pre_save, sender=stories_models.Role)
def on_role_pre_save(instance, **_kwargs):
    if instance.pk:
        old_role = stories_models.Role.objects.get(pk=instance.pk)
        instance.old_user = old_role.user


@dispatch.receiver(dj_models.signals.post_save, sender=stories_models.Role)
def on_role_save(instance, created, **_kwargs):
    game = game_models.Game.objects.filter(
        variation=instance.variation).first()
    if created or (not game) or (
            game.status < game_models.GAME_STATUS_IN_PROGRESS):
        return
    if instance.old_user != instance.user:
        mutations.UpdateRights(instance.variation.thread).apply()


class BaseGrantedRightsAPI(
        views.BaseGrantedRightsAPI, threads_api.BaseThreadAPI):
    rights_model = models.GameThreadRight
    update_mutation = mutations.UpdateRights

    def create_right(self, data):
        obj = self.rights_model.objects.get_or_create(
            thread=self.obj, role_id=data['user']['id'],
            defaults={'access_level': data['access_level']}
        )[0]
        obj.access_level = obj.access_level | data['access_level']
        return obj


class GrantedRightsAPI(views.GrantedRightsAPI, BaseGrantedRightsAPI):
    pass


class GrantedRightAPI(views.GrantedRightAPI, BaseGrantedRightsAPI):
    pass


def init():
    pass
