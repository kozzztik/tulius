from django.conf.urls import patterns, url
# TODO: fix this when module moved
from tulius.forum.plugins import ForumPlugin, BasePluginView
from .views import RebuildNums, FixLastPost, FixHtml

class FixesPlugin(ForumPlugin):
    def init_core(self):
        super(FixesPlugin, self).init_core()
        self.templates['fixes'] = 'forum/fixes/success.haml'
        self.urlizer['Thread_get_fix_counters_url'] = self.get_fix_counters_url
    
    def get_fix_counters_url(self, thread):
        return self.reverse('rebuild_nums', thread.id)
    
    def get_urls(self):
        return patterns('',
            url(r'^rebuild_nums/(?P<post_id>\d+)/$', RebuildNums.as_view(plugin=self), name='rebuild_nums'),
            url(r'^rebuild_nums/$', RebuildNums.as_view(plugin=self), name='rebuild_nums'),
            url(r'^fix_last_post/$', FixLastPost.as_view(plugin=self), name='fix_last_post'),
            url(r'^fix_html/$', FixHtml.as_view(plugin=self), name='fix_html'),
        )