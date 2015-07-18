from __future__ import print_function

from django.core.management.base import NoArgsCommand
from django.conf import settings
import logging

class Command(NoArgsCommand):
    logger = logging.getLogger('installer')
    
    def handle_noargs(self, migrate_all=False, **options):
        self.logger.info('Start clearing...')
        print('Start clearing...')
        try:
            from django.utils.importlib import import_module
            installers = []
            for app_name in settings.INSTALLED_APPS:
                try:
                    installers += [(app_name, import_module('.installer', app_name))]
                except ImportError as exc:
                    msg = exc.args[0]
                    if not msg.startswith('No module named') or 'installer' not in msg:
                        raise
            if not installers:
                self.logger.info('No modules to clear.')
                print('No modules to clear.')
            for installer in installers:
                clear_proc = getattr(installer[1], 'clear', None)
                if clear_proc:
                    self.logger.debug("Clearing %s" % installer[0])
                    print("Clearing %s..." % installer[0])
                    rec_cleared = clear_proc() or 0
                    self.logger.debug("%s cleared. %s records deleted." % (installer[0], rec_cleared))
                    print("%s cleared. %s records deleted." % (installer[0], rec_cleared))
            if 'django.contrib.sessions' in settings.INSTALLED_APPS:
                clear_sessions = getattr(settings, 'INSTALLER_CLEAR_SESSIONS', True)
                if clear_sessions:
                    self.logger.debug("Clearing sessions...")
                    print("Clearing sessions...")
                    from django.core.management import call_command
                    call_command('cleanup')
            self.logger.info('Clearing finished.')
            print('Clearing finished.')
        except Exception as e:
            self.logger.error(e)
            raise