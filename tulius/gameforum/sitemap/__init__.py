from tulius.forum.sitemap import SitemapPlugin, ForumSitemap
from tulius.stories.models import Variation
from tulius.games.models import GAME_STATUS_COMPLETED_OPEN

class GameForumSitemap(ForumSitemap):
    def get_root_threads(self):
        models = self.site.models
        variations = Variation.objects.filter(game__status=GAME_STATUS_COMPLETED_OPEN)
        thread_ids = [variation.thread_id for variation in variations if variation.thread_id]
        threads = models.Thread.objects.filter(id__in=thread_ids)
        for thread in threads:
            thread.user_roles = []
            thread.admin = False
            thread.guest = True
        return threads
        
class GameSitemapPlugin(SitemapPlugin):
    sitemap_class = GameForumSitemap