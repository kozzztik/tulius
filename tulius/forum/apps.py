from django.apps import AppConfig


class ForumConfig(AppConfig):
    name = 'tulius.forum'
    verbose_name = "Forum"
    site = None

    def ready(self):
        from tulius.forum import site
        from .threads.plugin import ThreadsPlugin
        from .fixes.plugin import FixesPlugin
        from .rights.plugin import RightsPlugin

        self.site = site.ForumSite(
            plugins=(
                RightsPlugin,
                ThreadsPlugin,
                FixesPlugin,
            )
        )
        site.site = self.site
