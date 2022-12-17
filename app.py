import os

from django_asyncio.app import run_app

if os.path.exists('settings_production.py'):
    settings_file = 'settings_production'
else:
    settings_file = 'settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_file)

run_app()
