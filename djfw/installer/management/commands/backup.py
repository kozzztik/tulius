from django.core.management.base import BaseCommand

from djfw.installer.maintaince.backup import do_backup


class Command(BaseCommand):
        
    def handle(self, category_name, **options):
        do_backup(category_name)
            