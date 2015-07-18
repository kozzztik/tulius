from django.contrib.sitemaps import Sitemap
from .models import Game, GAME_STATUS_OPEN_FOR_REGISTRATION, GAME_STATUS_REGISTRATION_COMPLETED, GAME_STATUS_IN_PROGRESS,\
                    GAME_STATUS_FINISHING, GAME_STATUS_COMPLETED_OPEN

class GamesSitemap(Sitemap):
    changefreq = "daily"
    priority = 1.0

    def items(self):
        statuses = [GAME_STATUS_OPEN_FOR_REGISTRATION, 
                    GAME_STATUS_REGISTRATION_COMPLETED, 
                    GAME_STATUS_IN_PROGRESS, 
                    GAME_STATUS_FINISHING,
                    GAME_STATUS_COMPLETED_OPEN]
        return Game.objects.filter(show_announcement=True, status__in=statuses)
