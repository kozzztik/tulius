# Generated by Django 3.1.1 on 2020-10-06 10:06

from django.db import migrations
from django.conf import settings
from django import apps as django_apps
from tulius.forum.elastic_search import mapping


def migrate_data(apps, schema_editor):
    for app_name, model_name in settings.ELASTIC_MODELS:
        model = django_apps.apps.get_model(app_name, model_name)
        mapping.rebuild_index(model)


class Migration(migrations.Migration):
    initial = True
    atomic = False
    dependencies = [
        ('forum_threads', '0001_squashed_0004_auto_20201011_1318'),
        ('forum_comments', '0001_squashed_0002_auto_20200910_1215'),
        ('game_forum_threads', '0001_squashed_0006_auto_20201013_1740'),
        ('game_forum_comments', '0001_squashed_0008_auto_20201013_1308'),
        ('tulius', '0001_squashed_0003_user_stories_author'),
        ('stories', '0001_squashed_0002_auto_20200724_2142'),
    ]

    operations = [
        migrations.RunPython(migrate_data)
    ]
