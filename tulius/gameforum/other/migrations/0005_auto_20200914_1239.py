# Generated by Django 3.1.1 on 2020-09-14 09:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('game_forum_other', '0004_auto_20200914_1009'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='threadreadmark',
            name='not_readed_comment_id',
        ),
        migrations.RemoveField(
            model_name='threadreadmark',
            name='readed_comment_id',
        ),
    ]
