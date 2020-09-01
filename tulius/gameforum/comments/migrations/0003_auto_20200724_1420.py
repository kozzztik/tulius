# Generated by Django 2.2.13 on 2020-07-24 11:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
        ('game_forum_comments', '0002_migration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='editor',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='game_forum_comments_edited',
                to=settings.AUTH_USER_MODEL, verbose_name='edited by'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='parent',
            field=mptt.fields.TreeForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='comments', to='game_forum_threads.Thread',
                verbose_name='thread'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='reply',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='answers', to='game_forum_comments.Comment',
                verbose_name='reply to'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='user',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='game_forum_comments',
                to=settings.AUTH_USER_MODEL, verbose_name='author'),
        ),
    ]
