from . import models
from tulius.forum.sites import BaseForumSite


class ForumSite(BaseForumSite):
    _models = models
