import os
import django

from tulius.websockets import app


if os.path.exists('settings_production.py'):
    settings_file = 'settings_production'
else:
    settings_file = 'settings'

os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_file)
django.setup()
app.main()
