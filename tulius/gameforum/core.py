from tulius.forum.threads import models as forum_models
from tulius.gameforum.threads import models
from tulius.gameforum import models as game_forum_models
from tulius.gameforum.comments import models as comment_models


def create_game_forum(user, variation):
    title = variation.game.name if variation.game else variation.name
    thread = models.Thread(
        title=title, user=user,
        access_type=forum_models.THREAD_ACCESS_TYPE_OPEN,
        room=True, variation_id=variation.pk)
    thread.save()
    return thread


def copy_game_post(thread, new_parent, variation, role_links):
    sub_threads = models.Thread.objects.filter(parent=thread, deleted=False)
    rights = game_forum_models.GameThreadRight.objects.filter(thread=thread)
    old_thread = thread
    thread = models.Thread(
        title=old_thread.title, parent=new_parent,
        body=old_thread.body, room=old_thread.room, user=old_thread.user,
        access_type=old_thread.access_type,
        create_time=old_thread.create_time, closed=old_thread.closed,
        important=old_thread.important,
        media=old_thread.media, variation_id=variation.pk,
    )
    role_id = old_thread.role_id
    if role_id and (role_id in role_links):
        thread.role_id = role_links[role_id].id
    thread.save()
    if not new_parent:
        variation.thread = thread
        variation.save()
    thread.variation = variation
    for right in rights:
        right.id = None
        right.thread = thread
        if right.role_id and (right.role_id in role_links):
            right.role = role_links[right.role_id]
        right.save()
    for sub_post in sub_threads:
        copy_game_post(sub_post, thread, variation, role_links)

    if not old_thread.room:
        first_comment = None
        sub_comments = comment_models.Comment.objects.filter(
            parent=old_thread, deleted=False)
        for comment in sub_comments:
            new_comment = comment_models.Comment(
                parent=thread, title=comment.title, body=comment.body,
                user=comment.user, create_time=comment.create_time,
                media=comment.media, order=comment.order)
            new_comment.reply_id = first_comment
            if comment.role_id and (comment.role_id in role_links):
                new_comment.role_id = role_links[comment.role_id].id
            new_comment.save()
            if not first_comment:
                first_comment = new_comment.pk
    return thread


def copy_game_forum(variation, rolelinks, user):
    if not variation.thread:
        variation.thread = create_game_forum(user, variation)
        variation.save()
    thread = copy_game_post(variation.thread, None, variation, rolelinks)
    thread.title = variation.game.name
    thread.save()
    return thread
