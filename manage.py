#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    if os.path.exists('settings-production.py'):
        settings_file = 'settings-production'
    else:
        settings_file = 'settings'
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_file)

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
