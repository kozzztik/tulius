from django import urls
from django.utils.translation import ugettext_lazy as _

from djfw.cataloging.core import CatalogPage
from .catalog import games_catalog_page
from .models import GAME_STATUS_COMPLETED, GAME_STATUS_COMPLETED_OPEN


EDIT_GAME_PAGES_MAIN = 'edit_game_main'
EDIT_GAME_PAGES_TEXTS = 'edit_game_texts'
EDIT_GAME_PAGES_USERS = 'edit_game_users'
EDIT_GAME_PAGES_GRAPHICS = 'edit_game_graphics'
EDIT_GAME_PAGES_VARIATIONS = 'edit_game_variations'
EDIT_GAME_PAGES_ROLES = 'edit_game_roles'
EDIT_GAME_PAGES_ILLUSTRATIONS = 'edit_game_illustrations'
EDIT_GAME_PAGES_MATERIALS = 'edit_game_materials'
EDIT_GAME_PAGES_REQUEST_FORM = 'edit_game_request_form'
EDIT_GAME_PAGES_REQUESTS = 'edit_game_requests'
EDIT_GAME_PAGES_FORUM = 'edit_game_forum'
EDIT_GAME_PAGES_WINNERS = 'edit_game_winners'
GAME_GRAPHICS = 'story_pics'

EDIT_GAME_PAGES = (
    (_('main'), EDIT_GAME_PAGES_MAIN),
    (_('texts'), EDIT_GAME_PAGES_TEXTS),
    (_('users'), EDIT_GAME_PAGES_USERS),
    (_('graphics'), EDIT_GAME_PAGES_GRAPHICS),
    (_('roles'), EDIT_GAME_PAGES_ROLES),
    (_('illustrations'), EDIT_GAME_PAGES_ILLUSTRATIONS),
    (_('materials'), EDIT_GAME_PAGES_MATERIALS),
    (_('request form'), EDIT_GAME_PAGES_REQUEST_FORM),
    (_('requests'), EDIT_GAME_PAGES_REQUESTS),
    (_('forum'), EDIT_GAME_PAGES_FORUM),
)

URL_PREFIX = 'games:'


class EditGamePage(CatalogPage):
    def get_subpages_internal(self):
        def urlize(subpath):
            return urls.reverse(URL_PREFIX + subpath, args=(self.instance.pk,))
        subpages = [
            CatalogPage(name=name, url=urlize(url), parent=self)
            for (name, url) in EDIT_GAME_PAGES]
        if self.instance.status in [
                GAME_STATUS_COMPLETED, GAME_STATUS_COMPLETED_OPEN]:
            subpages = subpages + [
                CatalogPage(
                    name=_('winners'),
                    url=urlize(EDIT_GAME_PAGES_WINNERS),
                    parent=self)]
        return subpages

    def get_caption(self):
        return str(self.instance)

    def __init__(self, game):
        self.parent = games_catalog_page()
        self.name = "%s %s" % (str(_('edit')), game)
        self.url = game.get_edit_url()
        self.is_index = True
        self.instance = game


def EditGameSubpage(game, url=EDIT_GAME_PAGES_TEXTS):
    gamepage = EditGamePage(game)
    return gamepage.get_subpage(
        urls.reverse(URL_PREFIX + url, args=(game.pk,)))


class GameSubpage:
    page_url = None
    paging_class = EditGamePage

    def get_context_data(self, **kwargs):
        context = super(GameSubpage, self).get_context_data(**kwargs)
        gamepage = self.paging_class(self.object)
        context['catalog_page'] = gamepage.get_subpage(
            urls.reverse(URL_PREFIX + self.page_url, args=(self.object.pk,)))
        return context
