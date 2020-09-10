# Generated by Django 2.2.13 on 2020-09-04 09:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

import tulius.forum.other.models


class Migration(migrations.Migration):

    replaces = [
        ('game_forum_other', '0001_initial'),
        ('game_forum_other', '0002_migration'),
        ('game_forum_other', '0003_auto_20200724_1949'),
        ('game_forum_other', '0004_commentlike_data'),
        ('game_forum_other', '0005_migrate_likes'),
        ('game_forum_other', '0006_fix_like_variation_names')
    ]

    initial = True

    dependencies = [
        ('forum', '0004_auto_20200721_1825'),
        ('game_forum_threads', '0001_squashed_0007_rights_migration'),
        ('game_forum_comments', '0001_squashed_0006_deleted_comments'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ThreadReadMark',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True, serialize=False,
                    verbose_name='ID')),
                ('readed_comment_id', models.IntegerField()),
                ('not_readed_comment_id', models.IntegerField(
                    blank=True, db_index=True, null=True)),
                ('thread', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='read_marks', to='game_forum_threads.Thread',
                    verbose_name='thread')),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='game_forum_other_readed_threads',
                    to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'verbose_name': 'thread read mark',
                'verbose_name_plural': 'thread read marks',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CommentLike',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True, serialize=False,
                    verbose_name='ID')),
                ('comment', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='liked', to='game_forum_comments.Comment',
                    verbose_name='comment')),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='game_liked_comments',
                    to=settings.AUTH_USER_MODEL, verbose_name='user')),
                ('data', models.JSONField(
                    default=tulius.forum.other.models.default_json)),

            ],
            options={
                'verbose_name': 'comment like',
                'verbose_name_plural': 'comments likes',
            },
        ),
        migrations.CreateModel(
            name='VotingVote',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True, serialize=False,
                    verbose_name='ID')),
                ('choice', models.IntegerField(verbose_name='choice')),
                ('comment', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='votes', to='game_forum_comments.Comment',
                    verbose_name='comment')),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='game_voting_votes',
                    to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'verbose_name': 'voting vote',
                'verbose_name_plural': 'voting votes',
                'unique_together': {('user', 'comment')},
            },
        ),
        migrations.CreateModel(
            name='OnlineUser',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True, serialize=False,
                    verbose_name='ID')),
                ('visit_time', models.DateTimeField(
                    auto_now_add=True, verbose_name='visit time')),
                ('thread', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='visit_marks',
                    to='game_forum_threads.Thread', verbose_name='thread')),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='game_forum_visit',
                    to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'verbose_name': 'online user',
                'verbose_name_plural': 'online users',
                'unique_together': {('user', 'thread')},
            },
        ),
    ]
