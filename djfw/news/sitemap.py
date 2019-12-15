from django.contrib import sitemaps
from django.utils import timezone

from . import models


class NewsSitemap(sitemaps.Sitemap):
    changefreq = "daily"
    priority = 1.0

    def items(self):
        return models.NewsItem.objects.filter(is_published=True).filter(
            published_at__lt=timezone.now()).order_by('-published_at')

    def lastmod(self, obj):
        return obj.updated_at
