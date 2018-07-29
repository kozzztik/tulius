from django import http
from django.shortcuts import get_object_or_404

from tulius.games.models import Game
from tulius.stories.models import Variation
from tulius.forum.plugins import BasePluginView


class GameIndex(BasePluginView):
    def get(self, request, game_id, **kwargs):
        try:
            game_id = int(game_id)
        except:
            raise http.Http404()
        game = get_object_or_404(Game, id=game_id)
        if not game.read_right(request.user):
            raise http.Http404()
        variation = game.variation
        if not variation.thread:
            variation.thread = self.core.create_gameforum(
                request.user, game.variation)
            variation.save()
        parent_thread = game.variation.thread
        return http.HttpResponseRedirect(parent_thread.get_absolute_url)


class VariationIndex(BasePluginView):
    def get(self, request, variation_id, **kwargs):
        try:
            variation_id = int(variation_id)
        except:
            raise http.Http404()
        variation = get_object_or_404(Variation, id=variation_id)
        if variation.game:
            return http.HttpResponseRedirect(
                self.plugin.game_url(variation.game))
        if not variation.edit_right(request.user):
            raise http.Http404()
        if not variation.thread:
            variation.thread = self.core.create_gameforum(
                request.user, variation)
            variation.save()
        parent_thread = variation.thread
        return http.HttpResponseRedirect(parent_thread.get_absolute_url)


class Fix(BasePluginView):
    template_name = 'fix_games'

    def get(self, request, **kwargs):
        self.site.core.fix_games()
        return super(Fix, self).get(request, **kwargs)
