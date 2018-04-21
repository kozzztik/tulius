import os
import gevent.socket
import redis.connection
from ws4redis.uwsgi_runserver import uWSGIWebsocketServer

redis.connection.socket = gevent.socket
if os.path.exists('settings-production.py'):
    settings_file = 'settings-production'
else:
    settings_file = 'settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_file)
application = uWSGIWebsocketServer()