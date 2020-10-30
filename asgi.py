import os

from django.core.asgi import get_asgi_application

from tulius.websockets import middleware


if os.path.exists('settings_production.py'):
    settings_file = 'settings_production'
else:
    settings_file = 'settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_file)


application = get_asgi_application()
application = middleware.websockets(application)
