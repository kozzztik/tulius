import gc

from django.conf import settings
from django.db import migrations


def migrate_data(apps, schema_editor):
    OldThreadAccessRight = apps.get_model('forum', 'ThreadAccessRight')
    ThreadAccessRight = apps.get_model('forum_rights', 'ThreadAccessRight')
    count = 0
    total_count = OldThreadAccessRight.objects.all().count()
    for old_item in OldThreadAccessRight.objects.all().iterator(
            chunk_size=1000):
        new_item = ThreadAccessRight(
            pk=old_item.pk,
            access_level=old_item.access_level,
            thread_id=old_item.thread_id,
            user_id=old_item.user_id,
        )
        new_item.save(force_insert=True)
        count += 1
        if count % 1000 == 0:
            gc.collect()
            print(f'migrated {count} rights')
    found = ThreadAccessRight.objects.all().count()
    print(f'Rights migrated {count} of {total_count}, found {found}')


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('forum', '0004_auto_20200721_1825'),
        ('forum_rights', '0001_initial'),
        ('forum_threads', '0002_migration'),
    ]

    atomic = False

    operations = [
        migrations.RunPython(migrate_data)
    ]
