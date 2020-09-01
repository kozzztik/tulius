import gc

from django.conf import settings
from django.db import migrations, transaction
from tulius.forum.threads import models
from tulius.forum.threads import mutations
from tulius.forum.rights import mutations as rights_mutations
from tulius.forum.comments import mutations as comments_mutations

comments_mutations.init()


class Tmp(rights_mutations.UpdateRights):
    # to make usage of rights for linters
    pass


def migrate_data(apps, schema_editor):
    count = 0
    total_count = models.Thread.objects.filter(parent=None).count()
    for thread in models.Thread.objects.filter(parent=None).iterator(
            chunk_size=1000):
        with transaction.atomic():
            mutations.ThreadFixCounters(thread).apply()
        count += 1
        if count % 10 == 0:
            gc.collect()
            print(f'migrated {count} threads')
    print(f'Threads migrated {count} of {total_count}')


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('forum_threads', '0005_deleted_threads'),
        ('forum_comments', '0006_deleted_comments'),
    ]

    atomic = False

    operations = [
        migrations.RunPython(migrate_data)
    ]
