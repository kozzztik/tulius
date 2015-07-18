from django.contrib.sitemaps import Sitemap
from .models import FlatPage

class FlatPageSitemap(Sitemap):
    changefreq = "daily"
    priority = 1.0

    def items(self):
        return FlatPage.objects.filter(is_enabled=True).order_by('id')

    def lastmod(self, obj):
        return obj.updated_at