import gc

from django.conf import settings
from django.db import migrations, transaction
from tulius.gameforum.threads import models
from tulius.gameforum.threads import mutations
from tulius.gameforum.rights import mutations as rights_mutations
from tulius.gameforum.comments import views


class Tmp(views.CommentAPI):
    # just to use views module, originally it is needed to connect mutations
    pass


class Tmp2(rights_mutations.UpdateRights):
    # just to use views module, originally it is needed to connect mutations
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
        ('game_forum_threads', '0005_deleted_threads'),
        ('game_forum_comments', '0006_deleted_comments'),

    ]

    atomic = False

    operations = [
        migrations.RunPython(migrate_data)
    ]
