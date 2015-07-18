from django.utils.translation import ugettext_lazy as _
from tulius.catalog import index_catalog_page
from django.core.urlresolvers import reverse
from djfw.cataloging.core import CatalogPage

def stories_catalog_page():
    return CatalogPage(name=_('story catalog'), url=reverse('stories:index'), 
        parent=index_catalog_page, is_index=True)