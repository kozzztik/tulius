import datetime

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Calculates collapsed statistics for fast reports"
    usage_str = "Usage: ./manage.py collapse_statistisc day. Day may be " \
        "'last'(previous day), 'all'(recalc all) or date like '2014-01-01'."

    def handle(self, day, **options):
        from djfw.profiler.collapse import do_collapse
        if day == 'last':
            day = datetime.date.today() - datetime.timedelta(days=1)
        elif day == 'all':
            day = None
        else:
            day = datetime.date.strptime(day, "%Y-%m-%d")
        do_collapse(day)
