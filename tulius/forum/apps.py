from django.apps import AppConfig


class ForumConfig(AppConfig):
    name = 'tulius.forum'
    verbose_name = "Forum"
    site = None

    def ready(self):
        from .sites import ForumSite
        from .threads.plugin import ThreadsPlugin
        from .search.plugin import SearchPlugin
        from .comments.plugin import CommentsPlugin
        from .fixes.plugin import FixesPlugin
        from .voting.plugin import VotingPlugin
        from .readmarks.plugin import ReadMarksPlugin
        from .rights.plugin import RightsPlugin
        from .online_status import OnlineStatusPlugin
        from .sitemap import SitemapPlugin
        from .collapse_threads import CollapsingThreadsPlugin

        self.site = ForumSite(
            plugins=(
                RightsPlugin,
                ThreadsPlugin,
                CommentsPlugin,
                VotingPlugin,
                SearchPlugin,
                ReadMarksPlugin,
                OnlineStatusPlugin,
                SitemapPlugin,
                FixesPlugin,
                CollapsingThreadsPlugin
            )
        )
