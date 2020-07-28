import gc

from django.conf import settings
from django.db import migrations, transaction
from tulius.forum.threads import models
from tulius.forum.rights import mutations


def migrate_data(apps, schema_editor):
    count = 0
    total_count = models.Thread.objects.filter(parent=None).count()
    for thread in models.Thread.objects.filter(parent=None).iterator(
            chunk_size=1000):
        with transaction.atomic():
            mutations.UpdateRights(thread).apply()
        count += 1
        if count % 10 == 0:
            gc.collect()
            print(f'migrated {count} threads')
    print(f'Threads migrated {count} of {total_count}')


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('forum_threads', '0005_deleted_threads'),

    ]

    atomic = False

    operations = [
        migrations.RunPython(migrate_data)
    ]
