# Generated by Django 2.2.13 on 2020-07-24 11:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import jsonfield.fields
import tulius.forum.comments.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('game_forum_threads', '0002_migration'),
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
                ('data', jsonfield.fields.JSONField(
                    default=tulius.forum.comments.models.default_json)),
                ('media', jsonfield.fields.JSONField(
                    default=tulius.forum.comments.models.default_json)),
                ('role_id', models.IntegerField(blank=True, null=True)),
                ('edit_role_id', models.IntegerField(blank=True, null=True)),
                ('editor', models.IntegerField(
                    blank=True, null=True, db_column='editor_id')),
                ('parent', models.IntegerField(db_column='parent_id')),
                ('reply', models.IntegerField(
                    blank=True, null=True, db_column='reply_id')),
                ('user', models.IntegerField(db_column='user_id')),
            ],
            options={
                'verbose_name': 'comment',
                'verbose_name_plural': 'comments',
                'ordering': ['id'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CommentDeleteMark',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True, serialize=False,
                    verbose_name='ID')),
                ('description', models.TextField(
                    blank=True, null=True, verbose_name='description')),
                ('deleted', models.BooleanField(
                    default=True, verbose_name='deleted')),
                ('delete_time', models.DateTimeField(
                    auto_now_add=True, verbose_name='deleted at')),
                ('comment', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='delete_marks',
                    to='game_forum_comments.Comment', verbose_name='comment')),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='game_forum_comments_delete_marks',
                    to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'verbose_name': 'comment delete mark',
                'verbose_name_plural': 'comments delete marks',
                'abstract': False,
            },
        ),
    ]
