from tulius.forum import models
from tulius.gameforum import consts
from tulius.gameforum import models as game_forum_models


def create_game_forum(user, variation):
    title = variation.game.name if variation.game else variation.name
    thread = models.Thread(
        title=title, user=user,
        access_type=models.THREAD_ACCESS_TYPE_OPEN,
        room=True, plugin_id=consts.GAME_FORUM_SITE_ID)
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
        important=old_thread.important, plugin_id=consts.GAME_FORUM_SITE_ID,
        media=old_thread.media,
    )
    role_id = old_thread.data1
    if role_id and (role_id in role_links):
        thread.data1 = role_links[role_id].id
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
        sub_comments = models.Comment.objects.filter(
            parent=old_thread, deleted=False)
        for comment in sub_comments:
            new_comment = models.Comment(
                parent=thread, title=comment.title, body=comment.body,
                plugin_id=consts.GAME_FORUM_SITE_ID,
                user=comment.user, create_time=comment.create_time,
                media=comment.media)
            new_comment.reply_id = first_comment
            if comment.data1 and (comment.data1 in role_links):
                new_comment.data1 = role_links[comment.data1].id
            new_comment.save()
            if not first_comment:
                first_comment = new_comment.id
    return thread


def copy_game_forum(variation, rolelinks, user):
    if not variation.thread:
        variation.thread = create_game_forum(user, variation)
        variation.save()
    thread = copy_game_post(variation.thread, None, variation, rolelinks)
    thread.title = variation.game.name
    thread.save()
    return thread
