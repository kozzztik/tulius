from django import dispatch
from django import urls
from django.core import exceptions
from django.utils import html
from djfw.wysibb.templatetags import bbcodes

from tulius.forum import signals
from tulius.forum import models
from tulius.stories import models as stories_models
from tulius.gameforum import consts
from tulius.gameforum.threads import api as threads
from tulius.forum.comments import api as comments


def validate_image_data(variation, images_data):
    result = []
    for image_data in images_data:
        image = stories_models.Illustration.objects.get(
            id=image_data['id'])
        if (image.variation_id == variation.id) or (
                image.story_id == variation.story_id):
            result.append({
                'id': image.id,
                'title': image.name,
                'url': image.image.url if image.image else None,
                'thumb': image.thumb.url if image.thumb else None,
            })
    return result


@dispatch.receiver(signals.before_create_thread)
def before_create_thread(sender, thread, data, **kwargs):
    if (sender.plugin_id != consts.GAME_FORUM_SITE_ID) or thread.room:
        return
    images_data = data['media'].get('illustrations')
    if not images_data:
        return
    thread.media['illustrations'] = validate_image_data(
        sender.variation, images_data)


@dispatch.receiver(signals.before_add_comment)
def before_add_comment(sender, comment, data, **kwargs):
    if sender.plugin_id != consts.GAME_FORUM_SITE_ID:
        return
    if sender.obj.first_comment_id is None:
        comment.data1 = sender.obj.data1
    images_data = data['media'].get('illustrations')
    if not images_data:
        return
    if sender.obj.first_comment_id == comment.id:
        comment.media['illustrations'] = sender.obj.media['illustrations']
    else:
        comment.media['illustrations'] = validate_image_data(
            sender.variation, images_data)


@dispatch.receiver(signals.on_comment_update)
def on_comment_update(sender, comment, data, **kwargs):
    if sender.plugin_id != consts.GAME_FORUM_SITE_ID:
        return
    if sender.obj.first_comment_id == comment.id:
        comment.data1 = sender.obj.data1
        comment.data2 = sender.obj.data2
    images_data = data['media'].get('illustrations')
    orig_data = comment.media.get('illustrations')
    if images_data:
        images_data = validate_image_data(sender.variation, images_data)
    if orig_data and not images_data:
        del comment.media['illustrations']
    elif images_data:
        comment.media['illustrations'] = images_data
    if sender.obj.first_comment_id == comment.id:
        if (not images_data) and ('illustrations' in sender.obj.media):
            del sender.obj.media['illustrations']
        elif images_data:
            sender.obj.media['illustrations'] = images_data


@dispatch.receiver(signals.thread_room_to_json)
def room_to_json(sender, thread, response, **kwargs):
    if thread.plugin_id != consts.GAME_FORUM_SITE_ID:
        return
    if thread.last_comment_id is None:
        return
    try:
        last_comment = models.Comment.objects.select_related('user').get(
            id=thread.last_comment_id)
    except models.Comment.DoesNotExist:
        return
    response['last_comment'] = {
        'id': last_comment.id,
        'thread': {
            'id': last_comment.parent_id,
            'url': sender.thread_url(last_comment.parent_id)
        },
        'page': last_comment.page,
        'user': sender.role_to_json(last_comment.data1),
        'create_time': last_comment.create_time,
    }


class CommentsBase(threads.BaseThreadAPI, comments.CommentsBase):
    def comment_url(self, comment):
        return urls.reverse(
            'game_forum_api:comment', kwargs={
                'pk': comment.id,
                'variation_id': self.variation.id,
            })

    def comment_to_json(self, c):
        data = {
            'id': c.id,
            'thread': {
                'id': c.parent_id,
                'url': self.thread_url(c.parent_id)
            },
            'page': c.page,
            'url': self.comment_url(c) if c.id else None,
            'title': html.escape(c.title),
            'body': bbcodes.bbcode(c.body),
            'user': self.role_to_json(c.data1, detailed=True),
            'create_time': c.create_time,
            'edit_right': self.comment_edit_right(c),
            'is_thread': c.is_thread(),
            'edit_time': c.edit_time,
            'editor': self.role_to_json(c.data2) if c.editor else None,
            'media': c.media,
            'reply_id': c.reply_id,

        }
        signals.comment_to_json.send(self, comment=c, data=data)
        return data


class CommentsPageAPI(comments.CommentsPageAPI, CommentsBase):
    def create_comment(self, text, data):
        comment = super(CommentsPageAPI, self).create_comment(text, data)
        comment.data1 = self.process_role(None, data)
        return comment


class CommentAPI(comments.CommentAPI, CommentsBase):
    def get_context_data(self, **kwargs):
        data = super(CommentAPI, self).get_context_data(**kwargs)
        data['thread']['rights'] = self.rights.to_json()
        return data

    def update_comment(self, comment, data):
        super(CommentAPI, self).update_comment(comment, data)
        new_role = data['role_id']
        if comment.data1 != new_role:
            if new_role not in self.rights.user_write_roles:
                raise exceptions.PermissionDenied()
            comment.data1 = new_role
        editor_role = data['edit_role_id']
        if editor_role not in self.rights.user_write_roles:
            raise exceptions.PermissionDenied()
        comment.data2 = editor_role
