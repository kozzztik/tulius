# Generated by Django 2.2.13 on 2020-09-04 10:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import mptt.fields


class Migration(migrations.Migration):

    replaces = [
        ('forum_threads', '0001_initial'),
        ('forum_threads', '0002_migration'),
        ('forum_threads', '0003_migrate_delete_marks'),
        ('forum_threads', '0004_delete_threaddeletemark'),
        ('forum_threads', '0005_deleted_threads'),
        ('forum_threads', '0006_rights_checker'),
        ('forum_threads', '0007_rights_migration')
    ]

    initial = True

    dependencies = [
        ('forum', '0004_auto_20200721_1825'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Thread',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True, serialize=False,
                    verbose_name='ID')),
                ('title', models.CharField(
                    max_length=255, verbose_name='title')),
                ('body', models.TextField(verbose_name='body')),
                ('room', models.BooleanField(
                    default=False, verbose_name='room')),
                ('default_rights', models.SmallIntegerField(
                    blank=True, choices=[
                        (None, 'access not set'), (3, 'free access'),
                        (1, 'read only access'),
                        (17, 'read only access(no inherit)'),
                        (0, 'private(no access)')],
                    default=None, null=True, verbose_name='access type')),
                ('create_time', models.DateTimeField(
                    auto_now_add=True, verbose_name='created at')),
                ('closed', models.BooleanField(
                    default=False, verbose_name='closed')),
                ('important', models.BooleanField(
                    default=False, verbose_name='important')),
                ('deleted', models.BooleanField(
                    default=False, verbose_name='deleted')),
                ('data', models.JSONField(default=dict)),
                ('media', models.JSONField(default=dict)),
                ('lft', models.PositiveIntegerField(
                    db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(
                    db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(
                    db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(
                    db_index=True, editable=False)),
                ('parent', mptt.fields.TreeForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='children', to='forum_threads.Thread',
                    verbose_name='parent thread')),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='forum_threads', to=settings.AUTH_USER_MODEL,
                    verbose_name='author')),
            ],
            options={
                'verbose_name': 'thread',
                'verbose_name_plural': 'threads',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='ThreadCollapseStatus',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True, serialize=False,
                    verbose_name='ID')),
                ('collapse_threads', models.BooleanField(default=False)),
                ('collapse_rooms', models.BooleanField(default=False)),
                ('thread', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    to='forum_threads.Thread', verbose_name='thread')),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'verbose_name': 'thread access right',
                'verbose_name_plural': 'threads access rights',
                'unique_together': {('thread', 'user')},
            },
        ),
    ]