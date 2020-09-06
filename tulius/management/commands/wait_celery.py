import time

from django.core.management.base import BaseCommand

from tulius import celery


class Command(BaseCommand):
    def handle(self, *args, **options):
        while True:
            active = celery.app.control.inspect().active()
            names = []
            for worker in active.values():
                names += [t['name'] for t in worker]
            if not names:
                print('No active tasks')
                break
            self.stdout.write(f'{len(names)} tasks active: {names}')
            self.stdout.write('Wait 15 seconds...')
            time.sleep(15)
