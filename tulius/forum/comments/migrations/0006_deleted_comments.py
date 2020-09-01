import gc

from django.conf import settings
from django.db import migrations


def migrate_data(apps, schema_editor):
    Thread = apps.get_model('forum_threads', 'Thread')
    Comment = apps.get_model('forum_comments', 'Comment')
    count = 0
    threads_count = 0
    total_count = Thread.objects.filter(deleted=True).count()
    print(f'start migrating {total_count} thread comments')
    for thread in Thread.objects.filter(deleted=True).iterator(
            chunk_size=1000):
        count += Comment.objects.filter(
            parent=thread, deleted=False).update(deleted=True)
        threads_count += 1
        gc.collect()
        if threads_count % 100 == 0:
            print(f'migrated {threads_count} threads with {count} comments')
    print(f'Comments migrated {count} of {total_count} threads')


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('forum_comments', '0005_delete_commentdeletemark'),
        ('forum_threads', '0005_deleted_threads'),
    ]

    atomic = False

    operations = [
        migrations.RunPython(migrate_data)
    ]
