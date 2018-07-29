from django.contrib import sitemaps
from . import models


class FlatPageSitemap(sitemaps.Sitemap):
    changefreq = "daily"
    priority = 1.0

    def items(self):
        return models.FlatPage.objects.filter(is_enabled=True).order_by('id')

    def lastmod(self, obj):
        return obj.updated_at
