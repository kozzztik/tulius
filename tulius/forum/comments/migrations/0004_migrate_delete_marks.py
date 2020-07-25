import gc

from django.conf import settings
from django.db import migrations


def migrate_data(apps, schema_editor):
    CommentDeleteMark = apps.get_model('forum_comments', 'CommentDeleteMark')
    count = 0
    total_count = CommentDeleteMark.objects.all().count()
    for old_mark in CommentDeleteMark.objects.all().iterator(chunk_size=1000):
        comment = old_mark.comment
        comment.data['deleted'] = {
            'user_id': old_mark.user_id,
            'time': old_mark.delete_time.isoformat(),
            'description': old_mark.description,
        }
        comment.save()
        count += 1
        if count % 1000 == 0:
            gc.collect()
            print(f'migrated {count} delete marks')
    found = CommentDeleteMark.objects.all().count()
    print(f'Delete marks migrated {count} of {total_count}, found {found}')


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('forum_comments', '0003_auto_20200724_1122'),
    ]

    atomic = False

    operations = [
        migrations.RunPython(migrate_data)
    ]
