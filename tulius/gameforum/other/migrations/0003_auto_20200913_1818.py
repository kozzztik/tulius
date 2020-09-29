# Generated by Django 3.1.1 on 2020-09-13 15:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('game_forum_other', '0002_auto_20200910_1230'),
    ]

    operations = [
        migrations.AddField(
            model_name='threadreadmark',
            name='not_read_comment_id',
            field=models.IntegerField(
                blank=True, db_index=True, null=True),
        ),
        migrations.AlterField(
            model_name='threadreadmark',
            name='user',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='game_forum_other_read_marks',
                to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterModelOptions(
            name='threadreadmark',
            options={},
        ),
        migrations.RemoveField(
            model_name='threadreadmark',
            name='readed_comment_id',
        ),
    ]