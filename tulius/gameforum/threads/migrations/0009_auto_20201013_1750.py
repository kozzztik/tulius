# Generated by Django 3.1.1 on 2020-10-13 14:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stories', '0001_squashed_0002_auto_20200724_2142'),
        ('game_forum_threads', '0008_auto_20201013_1748'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='thread',
            name='tmp1',
        ),
        migrations.RemoveField(
            model_name='thread',
            name='tmp2',
        ),
        migrations.RemoveField(
            model_name='thread',
            name='tmp3',
        ),
        migrations.AlterField(
            model_name='thread',
            name='variation',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='threads', to='stories.variation'),
        ),
    ]