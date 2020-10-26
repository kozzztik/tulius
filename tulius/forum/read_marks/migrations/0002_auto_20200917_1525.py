# Generated by Django 3.1.1 on 2020-09-17 12:25

import gc

from django.db import migrations


def migrate_data(apps, schema_editor):
    OldThreadReadMark = apps.get_model('forum_other', 'ThreadReadMark')
    ThreadReadMark = apps.get_model('forum_read_marks', 'ThreadReadMark')
    count = 0
    total_count = OldThreadReadMark.objects.all().count()
    print(f'Migrate {total_count} read marks')
    for old in OldThreadReadMark.objects.all().iterator(chunk_size=1000):
        if old.thread.deleted:
            continue
        read_mark = ThreadReadMark.objects.get_or_create(
            thread_id=old.thread_id,
            user_id=old.user_id,
            not_read_comment_id=old.not_readed_comment_id,
        )[0]
        for parent_id in read_mark.thread.parents_ids:
            item = ThreadReadMark.objects.get_or_create(
                thread_id=parent_id, user_id=read_mark.user_id,
                defaults={
                    'not_read_comment_id': read_mark.not_read_comment_id,
                }
            )[0]
            pk = read_mark.not_read_comment_id
            if (not item.not_read_comment_id) or (
                    pk and (item.not_read_comment_id > pk)):
                item.not_read_comment_id = pk
            item.save()
        count += 1
        if count % 1000 == 0:
            gc.collect()
            print(f'migrated {count} read marks')
    print(f'Read marks migrated {count} of {total_count}')


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('forum_read_marks', '0001_initial'),
        ('forum_other', '0001_squashed_0005_migrate_likes'),
        ('forum_threads', '0003_auto_20200912_1840'),
    ]

    operations = [
        migrations.RunPython(migrate_data)
    ]
