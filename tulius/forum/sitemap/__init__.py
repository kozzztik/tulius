from django.conf import urls
from django.contrib import sitemaps
from django.contrib.auth import models
from django.contrib.sitemaps import views

from tulius.forum import plugins


class ForumSitemap(sitemaps.Sitemap):
    changefreq = "daily"
    priority = 0.5

    def __init__(self, site, *args, **kwargs):
        super(ForumSitemap, self).__init__(*args, **kwargs)
        self.site = site
        self.user = models.AnonymousUser()

    def get_root_threads(self):
        site_models = self.site.models
        return site_models.Thread.objects.filter(
            parent=None, plugin_id=self.site.site_id,
            access_type__lt=site_models.THREAD_ACCESS_TYPE_NO_READ)

    def items(self):
        root_threads = self.get_root_threads()
        threads = []
        for thread in root_threads:
            thread.view_user = self.user
            subrooms, subthreads = self.site.core.room_descendants(
                self.user, thread)
            threads.append(thread)
            threads += subrooms
            threads += subthreads
        return threads

    def lastmod(self, obj):
        return obj.create_time

    def location(self, obj):
        return obj.get_absolute_url


class SitemapPlugin(plugins.ForumPlugin):
    sitemap_class = ForumSitemap

    def init_core(self):
        super(SitemapPlugin, self).init_core()
        self.core['sitemap'] = self.get_sitemap

    def get_sitemap(self):
        return self.sitemap_class(self.site)

    def sitemaps(self):
        return {'threads':  self.sitemap_class(self.site)}

    def get_urls(self):
        return [
            urls.url(
                r'^sitemap\.xml$',
                views.sitemap,
                {'sitemaps': self.sitemaps()},
                name='sitemap')
        ]
