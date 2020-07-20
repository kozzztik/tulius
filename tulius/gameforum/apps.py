from django.apps import AppConfig


class GameForumConfig(AppConfig):
    name = 'tulius.gameforum'
    verbose_name = "Game forum"

    def ready(self):
        pass
