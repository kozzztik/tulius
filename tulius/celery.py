import os
import logging

from celery import Celery, Task

import sentry_sdk


BASE_DIR = os.path.dirname(os.path.dirname(__file__)) + '/'
path = os.path.join(BASE_DIR, 'settings_production.py')
settings_file = 'settings_production' if os.path.exists(path) else 'settings'

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_file)


# pylint: disable=abstract-method
class LogErrorsTask(Task):
    # pylint: disable=too-many-arguments
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger = logging.getLogger('celery.task')
        logger.exception(exc, exc_info=exc)
        sentry_sdk.capture_exception(exc)
        super().on_failure(exc, task_id, args, kwargs, einfo)


class TuliusCelery(Celery):
    task_cls = LogErrorsTask


app = TuliusCelery('tulius')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


def init():
    pass
