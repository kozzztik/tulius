from django.apps import AppConfig


class ForumReadMarksConfig(AppConfig):
    name = 'tulius.forum.read_marks'
    label = 'forum_read_marks'

    def ready(self):
        from tulius.forum.read_marks import mutations
        mutations.init()
