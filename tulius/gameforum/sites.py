from tulius.forum.sites import BaseForumSite

from . import models


class GameForumSite(BaseForumSite):
    _models = models
    gamemodels = models

    def init_core(self):
        super(GameForumSite, self).init_core()
        self.templates['base'] = 'gameforum/base.haml'
        self.templates['actions'] = \
            'gameforum/snippets/forum_actions_menu.haml'
