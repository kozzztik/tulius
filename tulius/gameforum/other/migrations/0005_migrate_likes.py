import gc

from django import http
from django.conf import settings
from django.db import migrations
from django.core import exceptions

from tulius.gameforum.other import views
from tulius.gameforum.other import models as other_models
from tulius.stories import models as story_models


def migrate_data(apps, schema_editor):
    CommentLike = other_models.CommentLike
    count = 0
    total_count = CommentLike.objects.all().count()
    for item in CommentLike.objects.all().iterator(chunk_size=1000):
        view = views.Likes()
        view.setup(None)
        view.comment = item.comment
        view.user = item.user
        tree_id = view.comment.parent.tree_id
        view.variation = story_models.Variation.objects.get(
            thread__tree_id=tree_id)
        try:
            view.get_parent_thread(pk=view.comment.parent_id)
        except exceptions.PermissionDenied:
            print(f'permission denied on {item.id}')
            item.delete()
            continue
        except http.Http404:
            print(f'not found on {item.id} {view.comment.parent_id}')
            item.delete()
            continue
        item.data['comment'] = view.comment_to_json(view.comment)
        item.data['thread'] = view.obj_to_json()
        item.data['variation'] = {
            'id': view.variation.pk, 'name': view.variation.name}
        item.save()
        count += 1
        if count % 500 == 0:
            gc.collect()
            print(f'CommentLike migrated {count}')
    print(f'CommentLike migrated {count} of {total_count}')


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('game_forum_other', '0004_commentlike_data'),
        ('tulius', '0003_user_stories_author'),
    ]

    atomic = False

    operations = [
        migrations.RunPython(migrate_data)
    ]
