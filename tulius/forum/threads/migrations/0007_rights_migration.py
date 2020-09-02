import gc

from django.conf import settings
from django.db import migrations, transaction
from tulius.forum.threads import models
from tulius.forum.rights import mutations as rights_mutations
from tulius.forum.comments import mutations as comments_mutations

comments_mutations.init()


def migrate_thread(thread, rights_mask):
    if thread.default_rights is not None:
        rights_mask = thread.default_rights = \
            thread.default_rights & rights_mask
        thread.save()
    threads = models.Thread.objects.filter(parent=thread, deleted=False)
    for thread in threads:
        migrate_thread(thread, rights_mask)


def migrate_data(apps, schema_editor):
    count = 0
    for thread in models.Thread.objects.filter(
            parent=None).iterator(chunk_size=10):
        migrate_thread(thread, 3)
        with transaction.atomic():
            rights_mutations.UpdateRights(thread).apply()
        gc.collect()
        count += 1
        if count % 10 == 0:
            gc.collect()
            print(f'migrated {count} threads')


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('forum_threads', '0006_rights_checker'),
    ]

    atomic = False

    operations = [
        migrations.RunPython(migrate_data)
    ]
