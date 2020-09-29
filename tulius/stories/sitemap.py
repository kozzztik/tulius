from django.contrib.sitemaps import Sitemap
from .models import Story


class StoriesSitemap(Sitemap):
    changefreq = "daily"
    priority = 1.0

    def items(self):
        return Story.objects.filter(hidden=False)
