from django.apps import AppConfig


class ForumOtherConfig(AppConfig):
    name = 'tulius.forum.other'
    label = 'forum_other'

    def ready(self):
        # import to connect to signals
        from tulius.forum.other import youtube
        youtube.init()
