import gc

from django import http
from django.conf import settings
from django.db import migrations
from django.core import exceptions

from tulius.forum.other import likes
from tulius.forum.other import models as other_models


def migrate_data(apps, schema_editor):
    CommentLike = other_models.CommentLike
    count = 0
    total_count = CommentLike.objects.all().count()
    for item in CommentLike.objects.all().iterator(chunk_size=1000):
        view = likes.Likes()
        view.setup(None)
        view.comment = item.comment
        view.user = item.user
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
        item.data['thread'] = view.obj_to_json()  # pylint: disable=E1137
        item.save()
        count += 1
        if count % 1000 == 0:
            gc.collect()
            print(f'CommentLike migrated {count}')
    print(f'CommentLike migrated {count} of {total_count}')


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('forum_other', '0004_commentlike_data'),
        ('tulius', '0003_user_stories_author'),
        ('forum_threads', '0006_rights_checker'),
    ]

    atomic = False

    operations = [
        migrations.RunPython(migrate_data)
    ]
