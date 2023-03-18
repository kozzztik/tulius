from django.core.management.base import BaseCommand

from tulius.core import elastic_indexer


class Command(BaseCommand):
    def handle(self, *args, **options):
        elastic_indexer.indexer.push_dead_queue()
