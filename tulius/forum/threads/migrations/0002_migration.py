import gc

from django.conf import settings
from django.db import migrations

ACCESS_READ = 1
ACCESS_WRITE = 2

access_to_default_rights = {
    3: 0,  # THREAD_ACCESS_TYPE_NO_READ
    2: ACCESS_READ,  # THREAD_ACCESS_TYPE_NO_WRITE
    1: ACCESS_READ + ACCESS_WRITE,  # THREAD_ACCESS_TYPE_OPEN
    0: None,  # THREAD_ACCESS_TYPE_NOT_SET
}


def migrate_data(apps, schema_editor):
    OldThread = apps.get_model('forum', 'Thread')
    Thread = apps.get_model('forum_threads', 'Thread')
    count = 0
    total_count = OldThread.objects.filter(plugin_id=None).count()
    for old_thread in OldThread.objects.filter(plugin_id=None).order_by(
            'level', 'lft').iterator(chunk_size=1000):
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
        )
        new_thread.save(force_insert=True)
        count += 1
        if count % 1000 == 0:
            gc.collect()
            print(f'migrated {count} threads')
    found = Thread.objects.all().count()
    print(f'Threads migrated {count} of {total_count}, found {found}')

    OldCollapse = apps.get_model('forum', 'ThreadCollapseStatus')
    Collapse = apps.get_model('forum_threads', 'ThreadCollapseStatus')
    count = 0
    total_count = OldCollapse.objects.all().count()
    for old_collapse in OldCollapse.objects.all().iterator(chunk_size=1000):
        new_collapse = Collapse(
            collapse_threads=old_collapse.collapse_threads,
            collapse_rooms=old_collapse.collapse_rooms,
            thread_id=old_collapse.thread_id,
            user_id=old_collapse.user_id)
        new_collapse.save(force_insert=True)
        count += 1
        if count % 1000 == 0:
            gc.collect()
            print(f'migrated {count} collapses')
    found = Collapse.objects.all().count()
    print(f'Collapse status migrated {count} of {total_count}, found {found}')

    OldThreadDeleteMark = apps.get_model('forum', 'ThreadDeleteMark')
    ThreadDeleteMark = apps.get_model('forum_threads', 'ThreadDeleteMark')
    count = 0
    total_count = OldThreadDeleteMark.objects.filter(
        thread__plugin_id=None).count()
    for old_mark in OldThreadDeleteMark.objects.filter(
            thread__plugin_id=None).iterator(chunk_size=1000):
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
        ('forum_threads', '0001_initial'),

    ]

    atomic = False

    operations = [
        migrations.RunPython(migrate_data)
    ]
