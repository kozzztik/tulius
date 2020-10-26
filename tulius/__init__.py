from django.apps import AppConfig

from tulius import celery


class TuliusConfig(AppConfig):
    name = 'tulius'
    label = 'tulius'

    def ready(self):
        # This will make sure the app is always imported when
        # Django starts so that shared_task will use this app.
        celery.init()
