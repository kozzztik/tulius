from tulius.forum.sites import BaseForumSite

from . import models


class ForumSite(BaseForumSite):
    _models = models
