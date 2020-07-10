# Generated by Django 2.2.13 on 2020-07-10 07:19

import re

from django.db import migrations


old_link = 'old.tulius.com'
new_link = 'tulius.danetka.ru'
regexp = re.compile(re.escape(old_link), re.IGNORECASE)


def update_thread_links(apps, schema_editor):
    Comment = apps.get_model('forum', 'Comment')
    Thread = apps.get_model('forum', 'Thread')
    migrated_tb = 0
    migrated_tt = 0
    migrated_cb = 0
    migrated_ct = 0
    migrated_t = 0
    migrated_c = 0
    for thread in Thread.objects.all().iterator():
        thread.title, count1 = regexp.subn(new_link, thread.title)
        migrated_tt += count1
        thread.body, count2 = regexp.subn(new_link, thread.body)
        migrated_tb += count2
        if count1 + count2:
            migrated_t += 1
            thread.save()
            print(thread)
    for comment in Comment.objects.all().iterator():
        comment.title, count1 = regexp.subn(new_link, comment.title)
        migrated_ct += count1
        comment.body, count2 = regexp.subn(new_link, comment.body)
        migrated_cb += count2
        if count1 + count2:
            migrated_c += 1
            comment.save()
            print(comment)
    print(f'Replaced in thread titles: {migrated_tt}')
    print(f'Replaced in thread body: {migrated_tb}')
    print(f'Total migrated threads {migrated_t}')
    print(f'Replaced in comment titles: {migrated_ct}')
    print(f'Replaced in comment body: {migrated_cb}')
    print(f'Total migrated comments {migrated_c}')


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('forum', '0007_auto_20200630_1059'),
    ]

    operations = [
        migrations.RunPython(update_thread_links),
    ]
