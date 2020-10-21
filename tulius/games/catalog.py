from django import urls
from django.utils.translation import gettext_lazy as _

from tulius.catalog import index_catalog_page
from djfw.cataloging.core import CatalogPage


def games_catalog_page():
    return CatalogPage(
        name=_('games'), url=urls.reverse('games:index'),
        parent=index_catalog_page, is_index=True)
