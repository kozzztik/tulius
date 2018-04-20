from tulius.forum.sites import ForumSite


class GameForumSite(ForumSite):
    def init_core(self):
        super(GameForumSite, self).init_core()
        from . import models
        self.core.gamemodels = models
        self.gamemodels = models
        self.templates['base'] = 'gameforum/base.haml'
        self.templates['actions'] = \
            'gameforum/snippets/forum_actions_menu.haml'
