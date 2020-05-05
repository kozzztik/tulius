from django.contrib.sitemaps import Sitemap

from . import models


class GamesSitemap(Sitemap):
    changefreq = "daily"
    priority = 1.0

    def items(self):
        statuses = [
            models.GAME_STATUS_OPEN_FOR_REGISTRATION,
            models.GAME_STATUS_REGISTRATION_COMPLETED,
            models.GAME_STATUS_IN_PROGRESS,
            models.GAME_STATUS_FINISHING,
            models.GAME_STATUS_COMPLETED_OPEN
        ]
        return models.Game.objects.filter(
            show_announcement=True, status__in=statuses)
