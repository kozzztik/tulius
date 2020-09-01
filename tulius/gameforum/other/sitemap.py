from tulius.forum.other import sitemap
from tulius.stories import models as stories_models
from tulius.games import models as games_models
from tulius.gameforum.threads import models


class GameForumSitemap(sitemap.ForumSitemap):
    thread_model = models.Thread

    def iterate_games(self):
        variations = stories_models.Variation.objects.filter(
            game__status=games_models.GAME_STATUS_COMPLETED_OPEN)
        thread_ids = [
            variation.thread_id
            for variation in variations if variation.thread_id]
        for thread in self.thread_model.objects.filter(id__in=thread_ids):
            yield from self.iterate_threads(thread)

    def items(self):
        return list(self.iterate_games())

    def location(self, obj):
        return f'/play/thread/{obj.pk}/'
