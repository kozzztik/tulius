from django import urls
from django.utils.translation import gettext_lazy as _

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
        super().__init__(
            parent=EditStoryPage(variation.story),
            name=str(variation),
            url=variation.get_absolute_url(),
            is_index=True,
        )
        self.instance = variation


class EditVariationSubpage(CatalogPage):
    def __init__(self, variation, name='', url='', parent=None):
        super().__init__(
            parent=parent or EditVariationPage(variation),
            name=name,
            url=urls.reverse('stories:' + url, args=(variation.pk,))
        )
        if not name:
            for page in EDIT_VARIATION_PAGES:
                if page[1] == url:
                    self.name = str(page[0])
        self.instance = variation
