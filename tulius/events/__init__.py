from django.apps import AppConfig


class EventsConfig(AppConfig):
    name = 'tulius.events'

    def ready(self):
        # pylint: disable=C0415
        from tulius.events import views
        # import to connect to signals
        views.init()
