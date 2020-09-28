# Generated by Django 3.1.1 on 2020-09-12 15:54

import gc

from django.db import migrations, transaction

from tulius.forum.threads import mutations as base_mutations
from tulius.forum.threads import signals
from tulius.gameforum.threads import models
from tulius.gameforum.threads import mutations
from tulius.gameforum.rights import mutations as rights_mutations
from tulius.forum.comments import mutations as comments_mutations


class FixComments(comments_mutations.FixCounters):
    def fix_comments(self, instance):
        comments = instance.comments.filter(deleted=False)
        comments_count = comments.count()
        first_comment = None
        last_comment = None
        if comments_count:
            first_comment = comments.order_by('id')[0].pk
            last_comment = comments.order_by('-id')[0].pk
        return first_comment, last_comment, comments_count


class FixMutation(mutations.ThreadFixCounters):
    pass


signals.apply_mutation.connect(
    rights_mutations.on_fix_counters, sender=FixMutation)
base_mutations.on_mutation(FixMutation)(FixComments)


def migrate_data(apps, schema_editor):
    count = 0
    total_count = models.Thread.objects.filter(parent=None).count()
    for thread in models.Thread.objects.filter(parent=None).iterator(
            chunk_size=1000):
        with transaction.atomic():
            print(thread.pk)
            FixMutation(thread).apply()
        count += 1
        gc.collect()
        print(f'migrated {count} threads')
    print(f'Threads migrated {count} of {total_count}')


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('game_forum_threads', '0002_auto_20200910_1216'),
        ('game_forum_comments', '0003_auto_20200913_1526'),
    ]

    operations = [
        migrations.RunPython(migrate_data)
    ]
