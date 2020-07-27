import gc

from django.conf import settings
from django.db import migrations


def migrate_data(apps, schema_editor):
    Thread = apps.get_model('forum_threads', 'Thread')
    count = 0
    total_count = Thread.objects.filter(deleted=True).count()
    for thread in Thread.objects.filter(deleted=True).order_by(
            'level', 'lft').iterator(chunk_size=1000):
        Thread.objects.filter(
            tree_id=thread.tree_id, lft__gte=thread.lft,
            lft__lte=thread.rght, deleted=False).update(deleted=True)
        count += 1
        if count % 1000 == 0:
            gc.collect()
            print(f'migrated {count} threads')
    found = Thread.objects.all().count()
    print(f'Threads migrated {count} of {total_count}, found {found}')


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('forum_threads', '0004_delete_threaddeletemark'),

    ]

    atomic = False

    operations = [
        migrations.RunPython(migrate_data)
    ]
