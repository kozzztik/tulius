# Generated by Django 2.2.13 on 2020-09-04 10:08

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import mptt.fields

import tulius.forum.comments.models


class Migration(migrations.Migration):

    replaces = [
        ('game_forum_comments', '0001_initial'),
        ('game_forum_comments', '0002_migration'),
        ('game_forum_comments', '0003_auto_20200724_1420'),
        ('game_forum_comments', '0004_migrate_delete_marks'),
        ('game_forum_comments', '0005_delete_commentdeletemark'),
        ('game_forum_comments', '0006_deleted_comments')
    ]

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('game_forum_threads', '0001_squashed_0007_rights_migration'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True, serialize=False,
                    verbose_name='ID')),
                ('title', models.CharField(
                    max_length=255, verbose_name='title')),
                ('body', models.TextField(verbose_name='body')),
                ('create_time', models.DateTimeField(
                    auto_now_add=True, verbose_name='created at')),
                ('edit_time', models.DateTimeField(
                    blank=True, null=True, verbose_name='edited at')),
                ('deleted', models.BooleanField(
                    default=False, verbose_name='deleted')),
                ('order', models.IntegerField(verbose_name='order')),
                ('data', models.JSONField(
                    default=tulius.forum.comments.models.default_json)),
                ('media', models.JSONField(
                    default=tulius.forum.comments.models.default_json)),
                ('role_id', models.IntegerField(blank=True, null=True)),
                ('edit_role_id', models.IntegerField(blank=True, null=True)),
                ('editor', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='game_forum_comments_edited',
                    to=settings.AUTH_USER_MODEL, verbose_name='edited by')),
                ('parent', mptt.fields.TreeForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='comments', to='game_forum_threads.Thread',
                    verbose_name='thread')),
                ('reply', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='answers', to='game_forum_comments.Comment',
                    verbose_name='reply to')),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='game_forum_comments',
                    to=settings.AUTH_USER_MODEL, verbose_name='author')),
            ],
            options={
                'verbose_name': 'comment',
                'verbose_name_plural': 'comments',
                'ordering': ['id'],
                'abstract': False,
            },
        ),
    ]
