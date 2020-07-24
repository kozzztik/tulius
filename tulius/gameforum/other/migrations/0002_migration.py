import gc

from django.conf import settings
from django.db import migrations


def migrate_online_users(apps):
    OldOnlineUser = apps.get_model('forum', 'OnlineUser')
    OnlineUser = apps.get_model('game_forum_other', 'OnlineUser')
    count = 0
    total_count = OldOnlineUser.objects.filter(
        thread__plugin_id=1).count()
    for old_item in OldOnlineUser.objects.filter(
            thread__plugin_id=1).iterator(chunk_size=1000):
        new_item = OnlineUser(
            pk=old_item.pk,
            visit_time=old_item.visit_time,
            thread_id=old_item.thread_id,
            user_id=old_item.user_id,
        )
        new_item.save(force_insert=True)
        count += 1
        if count % 1000 == 0:
            gc.collect()
            print(f'migrated {count} OnlineUser')
    found = OnlineUser.objects.all().count()
    print(f'OnlineUser migrated {count} of {total_count}, found {found}')


def migrate_data(apps, schema_editor):
    migrate_online_users(apps)
    OldVotingVote = apps.get_model('forum', 'VotingVote')
    VotingVote = apps.get_model('game_forum_other', 'VotingVote')
    count = 0
    total_count = OldVotingVote.objects.filter(
        comment__parent__plugin_id=1).count()
    for old_item in OldVotingVote.objects.filter(
            comment__parent__plugin_id=1).iterator(chunk_size=1000):
        new_item = VotingVote(
            pk=old_item.pk,
            choice=old_item.choice,
            comment_id=old_item.comment_id,
            user_id=old_item.user_id,
        )
        new_item.save(force_insert=True)
        count += 1
        if count % 1000 == 0:
            gc.collect()
            print(f'VotingVote migrated {count}')
    found = VotingVote.objects.all().count()
    print(f'VotingVote migrated {count} of {total_count}, found {found}')

    OldCommentLike = apps.get_model('forum', 'CommentLike')
    CommentLike = apps.get_model('game_forum_other', 'CommentLike')
    count = 0
    total_count = OldCommentLike.objects.filter(
        comment__parent__plugin_id=1).count()
    for old_item in OldCommentLike.objects.filter(
            comment__parent__plugin_id=1).iterator(chunk_size=1000):
        new_item = CommentLike(
            pk=old_item.pk,
            comment_id=old_item.comment_id,
            user_id=old_item.user_id,
        )
        new_item.save(force_insert=True)
        count += 1
        if count % 1000 == 0:
            gc.collect()
            print(f'CommentLike migrated {count}')
    found = CommentLike.objects.all().count()
    print(f'CommentLike migrated {count} of {total_count}, found {found}')

    OldThreadReadMark = apps.get_model('forum', 'ThreadReadMark')
    OldThread = apps.get_model('forum', 'Thread')
    ThreadReadMark = apps.get_model('game_forum_other', 'ThreadReadMark')
    count = 0
    threads_count = 0
    total_count = OldThreadReadMark.objects.filter(
        thread__plugin_id=1).count()
    print(f'Start migrating {total_count} read marks')
    for old_thread in OldThread.objects.filter(plugin_id=1).iterator(
            chunk_size=100):
        for old_item in OldThreadReadMark.objects.filter(
                thread=old_thread).order_by('id').iterator(chunk_size=1000):
            new_item = ThreadReadMark(
                pk=old_item.pk,
                not_readed_comment_id=old_item.not_readed_comment_id,
                readed_comment_id=old_item.readed_comment_id,
                thread=old_item.thread_id,
                user=old_item.user_id,
            )
            new_item.save(force_insert=True)
            count += 1
        threads_count += 1
        gc.collect()
        if threads_count % 10 == 0:
            print(f'migrated {threads_count} threads with {count} marks')
    found = ThreadReadMark.objects.all().count()
    print(f'ThreadReadMark migrated {count} of {total_count}, found {found}')


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('forum', '0004_auto_20200721_1825'),
        ('game_forum_comments', '0002_migration'),
        ('game_forum_threads', '0002_migration'),
        ('game_forum_other', '0001_initial'),
    ]

    atomic = False

    operations = [
        migrations.RunPython(migrate_data)
    ]
