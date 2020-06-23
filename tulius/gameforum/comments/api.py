from django import dispatch
from django import urls
from django.core import exceptions
from django.utils import html
from djfw.wysibb.templatetags import bbcodes

from tulius.forum import signals
from tulius.gameforum import consts
from tulius.gameforum.threads import api as threads
from tulius.forum.comments import api as comments


@dispatch.receiver(signals.thread_room_to_json)
def room_to_json(sender, thread, response, **kwargs):
    if thread.plugin_id != consts.GAME_FORUM_SITE_ID:
        return
    if thread.last_comment is None:
        return
    response['last_comment'] = {
        'id': thread.last_comment.id,
        'parent_id': thread.last_comment.parent_id,
        'page': thread.last_comment.page,
        'user': sender.role_to_json(thread.last_comment.data1),
        'create_time': thread.last_comment.create_time,
    }


class CommentsBase(threads.BaseThreadAPI, comments.CommentsBase):
    def comment_url(self, comment):
        return urls.reverse(
            'game_forum_api:comment', kwargs={
                'pk': comment.id,
                'variation_id': self.variation.id,
            })

    def comment_to_json(self, c):
        return {
            'id': c.id,
            'url': self.comment_url(c) if c.id else None,
            'title': html.escape(c.title),
            'body': bbcodes.bbcode(c.body),
            'user': self.role_to_json(c.data1, detailed=True),
            'create_time': c.create_time,
            'voting': c.voting,
            'edit_right': self.comment_edit_right(c),
            'is_thread': c.is_thread(),
            'edit_time': c.edit_time,
            'editor': self.role_to_json(c.data2) if c.editor else None,
            'media': c.media,
        }


class CommentsPageAPI(comments.CommentsPageAPI, CommentsBase):
    def process_role(self, init_role_id, data):
        role_id = data.get('role_id')
        if role_id:
            if role_id not in self.rights.all_roles:
                raise exceptions.PermissionDenied('Role does not exist')
            if role_id == init_role_id:
                return role_id
        if role_id not in self.rights.user_write_roles:
            raise exceptions.PermissionDenied('Role is not accessible here')
        return role_id

    def create_comment(self, text, data):
        comment = super(CommentsPageAPI, self).create_comment(text, data)
        comment.data1 = self.process_role(None, data)
        return comment


class CommentAPI(comments.CommentAPI, CommentsBase):
    pass
