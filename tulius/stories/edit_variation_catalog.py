from django import urls
from django.utils.translation import ugettext_lazy as _

from djfw.cataloging.core import CatalogPage
from .edit_story_cataloging import EditStoryPage


EDIT_VARIATION_PAGES_MAIN = 'variation'
EDIT_VARIATION_PAGES_ROLES = 'edit_variation_roles'
EDIT_VARIATION_PAGES_ILLUSTRATIONS = 'edit_variation_illustrations'
EDIT_VARIATION_PAGES_MATERIALS = 'edit_variation_materials'
EDIT_VARIATION_FORUM = 'edit_variation_forum'

EDIT_VARIATION_PAGES = (
    (_('main'), EDIT_VARIATION_PAGES_MAIN),
    (_('roles'), EDIT_VARIATION_PAGES_ROLES),
    (_('illustrations'), EDIT_VARIATION_PAGES_ILLUSTRATIONS),
    (_('materials'), EDIT_VARIATION_PAGES_MATERIALS),
    (_('forum'), EDIT_VARIATION_FORUM),
)


class EditVariationPage(CatalogPage):
    def get_subpages(self):
        return [
            EditVariationSubpage(self.instance, name, url, self)
            for (name, url) in EDIT_VARIATION_PAGES]

    def __init__(self, variation):
        self.parent = EditStoryPage(variation.story)
        self.name = str(variation)
        self.url = variation.get_absolute_url()
        self.is_index = True
        self.instance = variation


class EditVariationSubpage(CatalogPage):
    def __init__(self, variation, name='', url='', parent=None):
        if parent:
            self.parent = parent
        else:
            self.parent = EditVariationPage(variation)
        self.name = str(name)
        self.url = urls.reverse('stories:' + url, args=(variation.pk,))
        if not name:
            for page in EDIT_VARIATION_PAGES:
                if page[1] == url:
                    self.name = str(page[0])
        self.instance = variation
