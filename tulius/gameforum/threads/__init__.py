from django.apps import AppConfig


class GameForumThreadsConfig(AppConfig):
    name = 'tulius.gameforum.threads'
    label = 'game_forum_threads'
    verbose_name = 'Game forum threads'

    def ready(self):
        # rights receivers may not be connected in tests
        # pylint: disable=C0415
        from tulius.gameforum.rights import views
        views.init()
