import gc

from django.conf import settings
from django.db import migrations, transaction
from tulius.gameforum.threads import models
from tulius.gameforum.rights import mutations as rights_mutations
from tulius.gameforum.comments import views
from tulius.stories import models as story_models

class Tmp(views.CommentAPI):
    # just to use views module, originally it is needed to connect mutations
    pass


def migrate_thread(thread, rights_mask):
    if (thread.default_rights is not None) and thread.parent:
        rights_mask = thread.default_rights = \
            thread.default_rights & rights_mask
        thread.save()
    threads = models.Thread.objects.filter(parent=thread, deleted=False)
    for t in threads:
        migrate_thread(t, rights_mask)


def migrate_data(apps, schema_editor):
    count = 0
    for thread in models.Thread.objects.filter(
            parent=None).iterator(chunk_size=10):
        migrate_thread(thread, 3)
        variation = story_models.Variation.objects.get(pk=thread.variation_id)
        with transaction.atomic():
            rights_mutations.UpdateRights(thread, variation).apply()
        gc.collect()
        count += 1
        if count % 10 == 0:
            gc.collect()
            print(f'migrated {count} threads')


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('game_forum_threads', '0006_rights_checker'),
    ]

    atomic = False

    operations = [
        migrations.RunPython(migrate_data)
    ]
