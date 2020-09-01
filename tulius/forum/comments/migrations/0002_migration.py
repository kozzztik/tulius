import gc

from django.conf import settings
from django.db import migrations


def migrate_data(apps, schema_editor):
    OldComment = apps.get_model('forum', 'Comment')
    OldThread = apps.get_model('forum', 'Thread')
    Comment = apps.get_model('forum_comments', 'Comment')
    count = 0
    threads_count = 0
    total_count = OldComment.objects.filter(parent__plugin_id=None).count()
    print(f'start migrating {total_count} comments')
    for old_thread in OldThread.objects.filter(plugin_id=None).iterator(
            chunk_size=1000):
        order = 0
        for old_item in OldComment.objects.filter(parent=old_thread).order_by(
                'id').iterator(chunk_size=1000):
            new_item = Comment(
                pk=old_item.pk,
                title=old_item.title,
                body=old_item.body,
                create_time=old_item.create_time,
                edit_time=old_item.edit_time,
                deleted=old_item.deleted,
                order=order,
                data={},
                media=old_item.media,
                editor=old_item.editor_id,
                parent=old_item.parent_id,
                reply=old_item.reply_id,
                user=old_item.user_id,
            )
            new_item.media['likes'] = old_item.likes
            new_item.save(force_insert=True)
            if not new_item.deleted:
                order += 1
            count += 1
        threads_count += 1
        gc.collect()
        if threads_count % 100 == 0:
            print(f'migrated {threads_count} threads with {count} comments')
    found = Comment.objects.all().count()
    print(f'Comments migrated {count} of {total_count}, found {found}')

    OldCommentDeleteMark = apps.get_model('forum', 'CommentDeleteMark')
    CommentDeleteMark = apps.get_model('forum_comments', 'CommentDeleteMark')
    count = 0
    total_count = OldCommentDeleteMark.objects.filter(
        comment__parent__plugin_id=None).count()
    for old_item in OldCommentDeleteMark.objects.filter(
            comment__parent__plugin_id=None).iterator(chunk_size=1000):
        new_item = CommentDeleteMark(
            pk=old_item.pk,
            description=old_item.description,
            deleted=old_item.deleted,
            delete_time=old_item.delete_time,
            comment_id=old_item.comment_id,
            user_id=old_item.user_id,
        )
        new_item.save(force_insert=True)
        count += 1
        if count % 1000 == 0:
            gc.collect()
            print(f'migrated {count} delete marks')
    found = CommentDeleteMark.objects.all().count()
    print(f'Marks migrated {count} of {total_count}, found {found}')


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('forum', '0004_auto_20200721_1825'),
        ('forum_comments', '0001_initial'),
        ('forum_threads', '0002_migration'),
    ]

    atomic = False

    operations = [
        migrations.RunPython(migrate_data)
    ]
