import gc

from django.conf import settings
from django.db import migrations, transaction
from tulius.gameforum.threads import models
from tulius.gameforum.rights import mutations
from tulius.stories import models as stories_models


def migrate_data(apps, schema_editor):
    count = 0
    total_count = models.Thread.objects.filter(parent=None).count()
    for thread in models.Thread.objects.filter(parent=None).iterator(
            chunk_size=1000):
        variation = stories_models.Variation.objects.get(
            pk=thread.variation_id)
        with transaction.atomic():
            mutations.UpdateRights(thread, variation=variation).apply()
        count += 1
        if count % 10 == 0:
            gc.collect()
            print(f'migrated {count} threads')
    print(f'Threads migrated {count} of {total_count}')


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('game_forum_threads', '0005_deleted_threads'),

    ]

    atomic = False

    operations = [
        migrations.RunPython(migrate_data)
    ]
