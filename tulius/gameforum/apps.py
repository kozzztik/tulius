from django.apps import AppConfig


class GameForumConfig(AppConfig):
    name = 'gameforum'
    verbose_name = "Game forum"
    site = None
    GAME_FORUM_SITE_ID = 1

    def ready(self):
        from .sites import GameForumSite
        from tulius.forum.voting.plugin import VotingPlugin
        from tulius.forum.readmarks.plugin import ReadMarksPlugin
        from tulius.forum.fixes.plugin import FixesPlugin
        from .gamecore import GamePlugin
        from .trustmarks import TrustmarksPlugin
        from .rights import GameRightsPlugin
        from .search import GameSearchPlugin
        from .threads import GameThreadsPlugin
        from .comments import GameCommentsPlugin
        from .online_status import GameOnlineStatusPlugin
        from .sitemap import GameSitemapPlugin

        self.site = GameForumSite(
            name='gameforum',
            app_name='gameforum',
            site_id=self.GAME_FORUM_SITE_ID,
            plugins=(
                TrustmarksPlugin,
                GameRightsPlugin,
                GameThreadsPlugin,
                GameCommentsPlugin,
                VotingPlugin,
                GameSearchPlugin,
                ReadMarksPlugin,
                GameOnlineStatusPlugin,
                GamePlugin,
                GameSitemapPlugin,
                FixesPlugin
            )
        )
