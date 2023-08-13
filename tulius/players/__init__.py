from django.apps import AppConfig


class PlayersConfig(AppConfig):
    name = "tulius.players"
    label = 'players'
    verbose_name = "Players"

    def ready(self):
        from tulius.players.models import stars
        stars.flush_stars_cache()
