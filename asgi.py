import os

from django.conf import settings
from django.contrib.staticfiles import handlers as static_handlers

from django_asyncio.asgi_handler import get_asgi_application

if os.path.exists('settings_production.py'):
    settings_file = 'settings_production'
else:
    settings_file = 'settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_file)


application = get_asgi_application()

if settings.DEBUG:
    application = static_handlers.ASGIStaticFilesHandler(application)
