from __future__ import print_function

from django.core.management.base import NoArgsCommand
import logging

class Command(NoArgsCommand):
    logger = logging.getLogger('bugtracker')
    
    def handle_noargs(self, migrate_all=False, **options):
        self.logger.info('Start sync...')
        print('Start sync...')
        try:
            try:
                from djfw.bugtracker.atlassian.sync import sync_all
            except:
                from bugtracker.atlassian.sync import sync_all
            sync_all()
            self.logger.info('Synced.')
            print('Synced.')
        except Exception as e:
            self.logger.error(e)
            raise