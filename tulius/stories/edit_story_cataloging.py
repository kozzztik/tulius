from django import urls
from django.utils.translation import gettext_lazy as _

from tulius.stories.catalog import stories_catalog_page
from djfw.cataloging.core import CatalogPage


EDIT_STORY_PAGES_MAIN = 'edit_story_main'
EDIT_STORY_PAGES_TEXTS = 'edit_story_texts'
EDIT_STORY_PAGES_USERS = 'edit_story_users'
EDIT_STORY_PAGES_GRAPHICS = 'edit_story_graphics'
EDIT_STORY_PAGES_VARIATIONS = 'edit_story_variations'
EDIT_STORY_PAGES_CHARACTERS = 'edit_story_characters'
EDIT_STORY_PAGES_AVATARS = 'edit_story_avatars'
EDIT_STORY_PAGES_UPLOADS = 'edit_story_uploads'
EDIT_STORY_PAGES_ILLUSTRATIONS = 'edit_story_illustrations'
EDIT_STORY_PAGES_MATERIALS = 'edit_story_materials'
STORY_GRAPHICS = 'story_pics'

EDIT_STORY_PAGES = (
    (_('main'), EDIT_STORY_PAGES_MAIN),
    (_('texts'), EDIT_STORY_PAGES_TEXTS),
    (_('users'), EDIT_STORY_PAGES_USERS),
    (_('graphics'), EDIT_STORY_PAGES_GRAPHICS),
    (_('characters'), EDIT_STORY_PAGES_CHARACTERS),
    (_('avatars'), EDIT_STORY_PAGES_AVATARS),
    (_('illustrations'), EDIT_STORY_PAGES_ILLUSTRATIONS),
    (_('materials'), EDIT_STORY_PAGES_MATERIALS),
    (_('variations'), EDIT_STORY_PAGES_VARIATIONS),
)


class EditStoryPage(CatalogPage):
    def get_subpages(self):
        return [
            EditStorySubpage(self.instance, name, url, self)
            for (name, url) in EDIT_STORY_PAGES]

    def get_caption(self):
        return str(self.instance)

    def __init__(self, story):
        super().__init__(
            is_index=True,
            parent=stories_catalog_page(),
            name="%s %s" % (str(_('edit')), story),
            url=story.get_edit_url(),
        )
        self.instance = story


class EditStorySubpage(CatalogPage):
    def __init__(self, story, name='', url='', parent=None):
        super().__init__(
            parent=parent or EditStoryPage(story),
            name=name,
            url=urls.reverse('stories:' + url, args=(story.pk,)),
        )
        if not name:
            for page in EDIT_STORY_PAGES:
                if page[1] == url:
                    self.name = str(page[0])
        self.instance = story
