from django.apps import AppConfig

from tulius.forum.elastic_search import models


class ForumElasticSearchConfig(AppConfig):
    name = 'tulius.forum.elastic_search'
    label = 'forum_elastic_search'
    verbose_name = 'Forum indexing'

    def ready(self):
        models.init()
