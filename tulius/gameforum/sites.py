from tulius.forum.site import ForumSite

from . import models


class GameForumSite(ForumSite):
    gamemodels = models

    def init_core(self):
        super(GameForumSite, self).init_core()
        self.templates['base'] = 'gameforum/base.haml'
        self.templates['actions'] = \
            'gameforum/snippets/forum_actions_menu.haml'
