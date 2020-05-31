from django import http
from django.views import generic
from django.core import exceptions

from tulius.forum import models
from tulius.forum import plugins
from tulius.gameforum import consts
from tulius.stories import models as stories_models


class RedirrectAPI(generic.View):
    @staticmethod
    def get(*args, **kwargs):
        pk = int(kwargs['pk'])
        thread = models.Thread.objects.get(
            pk=pk, plugin_id=consts.GAME_FORUM_SITE_ID)
        if thread.parent_id is None:
            variation = stories_models.Variation.objects.get(
                thread=thread)
        else:
            variation = stories_models.Variation.objects.get(
                thread__tree_id=thread.tree_id)
        return http.JsonResponse({
            'variation_id': variation.id,
            'room': thread.room,
        })


class VariationAPI(plugins.BaseAPIView):
    obj = None

    def get_variation(self, **kwargs):
        self.obj = stories_models.Variation.objects.get(pk=kwargs['pk'])

    def check_rights(self):
        if self.obj.game:
            return self.obj.game.read_right(self.user)
        return self.obj.edit_right(self.user)

    def get_context_data(self, **kwargs):
        self.get_variation(**kwargs)
        if not self.check_rights():
            raise exceptions.PermissionDenied()
        return {
            'id': self.obj.id,
            'game': self.obj.game_id,
        }
