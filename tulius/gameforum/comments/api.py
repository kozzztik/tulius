from django import dispatch
from django import urls
from django.core import exceptions
from django.utils import html
from djfw.wysibb.templatetags import bbcodes

from tulius.forum import signals
from tulius.forum import models
from tulius.gameforum import consts
from tulius.gameforum.threads import api as threads
from tulius.forum.comments import api as comments


@dispatch.receiver(signals.before_add_comment)
def before_add_comment(sender, comment, **kwargs):
    if sender.plugin_id != consts.GAME_FORUM_SITE_ID:
        return
    if sender.obj.first_comment_id is None:
        comment.data1 = sender.obj.data1


@dispatch.receiver(signals.on_comment_update)
def on_comment_update(sender, comment, **kwargs):
    if sender.plugin_id != consts.GAME_FORUM_SITE_ID:
        return
    if sender.obj.first_comment_id == comment.id:
        comment.data1 = sender.obj.data1
        comment.data2 = sender.obj.data2


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
