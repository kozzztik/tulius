from django.contrib.sitemaps import Sitemap
from .models import TreePage

class TreePageSitemap(Sitemap):
    changefreq = "dayly"
    priority = 1.0

    def items(self):
        pages = TreePage.objects.filter(is_enabled=True).order_by('id')
        pages_dict = {}
        for page in pages:
            pages_dict[page.url] = page
        page_ids = [page.pk for page in pages_dict.itervalues()]
        return TreePage.objects.filter(pk__in=page_ids).order_by('id')

    def lastmod(self, obj):
        return obj.updated_at