import gc

from django import http
from django.conf import settings
from django.db import migrations
from tulius.gameforum.other import models as other_models
from tulius.stories import models as story_models


def migrate_data(apps, schema_editor):
    CommentLike = other_models.CommentLike
    count = 0
    total_count = CommentLike.objects.all().count()
    for item in CommentLike.objects.all().iterator(chunk_size=1000):
        variation = story_models.Variation.objects.get(
            pk=item.data['variation']['id'])
        item.data['variation']['name'] = \
            str(variation.game) if variation.game else variation.name
        item.save()
        count += 1
        if count % 500 == 0:
            gc.collect()
            print(f'CommentLike migrated {count}')
    print(f'CommentLike migrated {count} of {total_count}')


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('game_forum_other', '0005_migrate_likes'),
    ]

    atomic = False

    operations = [
        migrations.RunPython(migrate_data)
    ]
