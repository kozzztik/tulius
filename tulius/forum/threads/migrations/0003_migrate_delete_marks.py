import gc

from django.conf import settings
from django.db import migrations


def migrate_data(apps, schema_editor):
    ThreadDeleteMark = apps.get_model('forum_threads', 'ThreadDeleteMark')
    count = 0
    total_count = ThreadDeleteMark.objects.all().count()
    for old_mark in ThreadDeleteMark.objects.all().iterator(chunk_size=1000):
        thread = old_mark.thread
        thread.data['deleted'] = {
            'user_id': old_mark.user_id,
            'time': old_mark.delete_time.isoformat(),
            'description': old_mark.description,
        }
        thread.save()
        count += 1
        if count % 1000 == 0:
            gc.collect()
            print(f'migrated {count} delete marks')
    found = ThreadDeleteMark.objects.all().count()
    print(f'Delete marks migrated {count} of {total_count}, found {found}')


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('forum_threads', '0002_migration'),

    ]

    atomic = False

    operations = [
        migrations.RunPython(migrate_data)
    ]
