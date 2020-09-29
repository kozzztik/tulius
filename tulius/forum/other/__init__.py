from django.apps import AppConfig

from tulius.forum.other import youtube


class ForumOtherConfig(AppConfig):
    name = 'tulius.forum.other'
    label = 'forum_other'

    def ready(self):
        # import to connect to signals
        youtube.init()
