from django.apps import AppConfig

from tulius.websockets import runserver


class WebsocketsConfig(AppConfig):
    name = 'tulius.websockets'
    label = 'websockets'
    verbose_name = 'websockets'

    def ready(self):
        runserver.patch()
