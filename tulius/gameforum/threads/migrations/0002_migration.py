import gc

from django.conf import settings
from django.db import migrations

ACCESS_READ = 1
ACCESS_WRITE = 2
ACCESS_NO_INHERIT = 16

access_to_default_rights = {
    3: 0,  # THREAD_ACCESS_TYPE_NO_READ
    2: ACCESS_READ,  # THREAD_ACCESS_TYPE_NO_WRITE
    1: ACCESS_READ + ACCESS_WRITE,  # THREAD_ACCESS_TYPE_OPEN
    0: None,  # THREAD_ACCESS_TYPE_NOT_SET
}


def migrate_data(apps, schema_editor):
    OldThread = apps.get_model('forum', 'Thread')
    Thread = apps.get_model('game_forum_threads', 'Thread')
    Variation = apps.get_model('stories', 'Variation')
    count = 0
    total_count = OldThread.objects.filter(plugin_id=1).count()
    for old_thread in OldThread.objects.filter(plugin_id=1).order_by(
            'level', 'lft').iterator(chunk_size=1000):
        variation = Variation.objects.filter(
            thread__tree_id=old_thread.tree_id).first()
        if not variation:
            print(f'broken thread variation {old_thread.pk}')
            continue
        new_thread = Thread(
            pk=old_thread.pk,
            title=old_thread.title,
            body=old_thread.body,
            room=old_thread.room,
            default_rights=access_to_default_rights[old_thread.access_type],
            create_time=old_thread.create_time,
            closed=old_thread.closed,
            important=old_thread.important,
            deleted=old_thread.deleted,
            first_comment_id=old_thread.first_comment_id,
            last_comment_id=old_thread.last_comment_id,
            comments_count=old_thread.comments_count,
            data={},
            media=old_thread.media,
            lft=old_thread.lft,
            rght=old_thread.rght,
            tree_id=old_thread.tree_id,
            level=old_thread.level,
            parent_id=old_thread.parent_id,
            user_id=old_thread.user_id,
            role_id=old_thread.data1,
            edit_role_id=old_thread.data2,
            variation_id=variation.pk,
        )
        if (not new_thread.parent_id) and (
                new_thread.default_rights == ACCESS_READ):
            new_thread.default_rights = ACCESS_READ + ACCESS_NO_INHERIT
        new_thread.save(force_insert=True)
        count += 1
        if count % 1000 == 0:
            gc.collect()
            print(f'migrated {count} threads')
    found = Thread.objects.all().count()
    print(f'Threads migrated {count} of {total_count}, found {found}')

    OldThreadDeleteMark = apps.get_model('forum', 'ThreadDeleteMark')
    ThreadDeleteMark = apps.get_model('game_forum_threads', 'ThreadDeleteMark')
    count = 0
    total_count = OldThreadDeleteMark.objects.filter(
        thread__plugin_id=1).count()
    for old_mark in OldThreadDeleteMark.objects.filter(
            thread__plugin_id=1).iterator(chunk_size=1000):
        new_mark = ThreadDeleteMark(
            description=old_mark.description,
            deleted=old_mark.deleted,
            delete_time=old_mark.delete_time,
            thread_id=old_mark.thread_id,
            user_id=old_mark.user_id)
        new_mark.save(force_insert=True)
        count += 1
        if count % 1000 == 0:
            gc.collect()
            print(f'migrated {count} delete marks')
    found = ThreadDeleteMark.objects.all().count()
    print(f'Delete marks migrated {count} of {total_count}, found {found}')


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('forum', '0004_auto_20200721_1825'),
        ('game_forum_threads', '0001_initial'),
        ('stories', '0001_squashed_0002_auto_20180418_1722'),
    ]

    atomic = False

    operations = [
        migrations.RunPython(migrate_data)
    ]
