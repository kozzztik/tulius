from django.contrib.sitemaps import Sitemap
from django.utils.timezone import now
from .models import NewsItem

class NewsSitemap(Sitemap):
    changefreq = "daily"
    priority = 1.0

    def items(self):
        return NewsItem.objects.filter(is_published=True).filter(published_at__lt=now()).order_by('-published_at')

    def lastmod(self, obj):
        return obj.updated_at