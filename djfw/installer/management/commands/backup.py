from django.core.management.base import BaseCommand

from djfw.installer.maintaince.backup import do_backup


class Command(BaseCommand):

    def handle(self, *args, **options):
        category_name = options['category_name']
        do_backup(category_name)
