import os

from celery import Celery

BASE_DIR = os.path.dirname(os.path.dirname(__file__)) + '/'
path = os.path.join(BASE_DIR, 'settings_production.py')
settings_file = 'settings_production' if os.path.exists(path) else 'settings'

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_file)

app = Celery('tulius')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


def init():
    pass
