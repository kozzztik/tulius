from tulius.forum import sitemap
from tulius.games import models as games_models
from tulius.stories import models as stories_models


class GameForumSitemap(sitemap.ForumSitemap):
    def get_root_threads(self):
        models = self.site.models
        variations = stories_models.Variation.objects.filter(
            game__status=games_models.GAME_STATUS_COMPLETED_OPEN)
        thread_ids = [
            variation.thread_id
            for variation in variations if variation.thread_id]
        threads = models.Thread.objects.filter(id__in=thread_ids)
        for thread in threads:
            thread.user_roles = []
            thread.admin = False
            thread.guest = True
        return threads


class GameSitemapPlugin(sitemap.SitemapPlugin):
    sitemap_class = GameForumSitemap
