from django.apps import AppConfig

from tulius.gameforum import consts


class GameForumConfig(AppConfig):
    name = 'tulius.gameforum'
    verbose_name = "Game forum"
    site = None
    GAME_FORUM_SITE_ID = consts.GAME_FORUM_SITE_ID

    def ready(self):
        from .sites import GameForumSite
        from .gamecore import GamePlugin
        from .rights import GameRightsPlugin
        from .threads import GameThreadsPlugin

        self.site = GameForumSite(
            name='gameforum',
            app_name='gameforum',
            site_id=self.GAME_FORUM_SITE_ID,
            plugins=(
                GameRightsPlugin,
                GameThreadsPlugin,
                GamePlugin,
            )
        )
