from django.contrib import sitemaps

from tulius.forum.threads import models


class ForumSitemap(sitemaps.Sitemap):
    changefreq = "daily"
    priority = 0.5
    thread_model = models.Thread

    def iterate_threads(self, parent):
        items = self.thread_model.objects.filter(
            parent=parent, deleted=False,
            access_type__lt=models.THREAD_ACCESS_TYPE_NO_READ)
        for obj in items:
            if obj.room:
                yield from self.iterate_threads(obj)
            else:
                yield obj

    def items(self):
        return list(self.iterate_threads(None))

    def lastmod(self, obj):
        return obj.create_time

    def location(self, obj):
        return f'/forums/thread/{obj.pk}/'

    @classmethod
    def sitemaps(cls):
        return {'threads': cls()}
