from django.apps import AppConfig


class ForumCommentsConfig(AppConfig):
    name = 'tulius.forum.comments'
    label = 'forum_comments'

    def ready(self):
        # pylint: disable=C0415
        from tulius.forum.comments import mutations
        mutations.init()
