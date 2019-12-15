from django.conf import urls

from tulius.forum import plugins
from tulius.forum.fixes import views


class FixesPlugin(plugins.ForumPlugin):
    def init_core(self):
        super(FixesPlugin, self).init_core()
        self.templates['fixes'] = 'forum/fixes/success.haml'
        self.urlizer['Thread_get_fix_counters_url'] = self.get_fix_counters_url

    def get_fix_counters_url(self, thread):
        return self.reverse('rebuild_nums', thread.id)

    def get_urls(self):
        return [
            urls.url(
                r'^rebuild_nums/(?P<post_id>\d+)/$',
                views.RebuildNums.as_view(plugin=self),
                name='rebuild_nums'),
            urls.url(
                r'^rebuild_nums/$',
                views.RebuildNums.as_view(plugin=self),
                name='rebuild_nums'),
            urls.url(
                r'^fix_last_post/$',
                views.FixLastPost.as_view(plugin=self),
                name='fix_last_post'),
            urls.url(
                r'^fix_html/$',
                views.FixHtml.as_view(plugin=self),
                name='fix_html'),
        ]
