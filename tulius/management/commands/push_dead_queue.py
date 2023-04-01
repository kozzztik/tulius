from django.core.management.base import BaseCommand

from tulius.core.elastic import indexing


class Command(BaseCommand):
    def handle(self, *args, **options):
        indexing.get_indexer().push_dead_queue()
