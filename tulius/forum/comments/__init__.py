from django.apps import AppConfig


class ForumCommentsConfig(AppConfig):
    name = 'tulius.forum.comments'
    label = 'forum_comments'

    def ready(self):
        from tulius.forum.comments import mutations
        mutations.init()
