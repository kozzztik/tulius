import json

from django import dispatch
from django import shortcuts
from django.core import exceptions
from django.db import transaction
from django.utils import html
from djfw.wysibb.templatetags import bbcodes

from tulius.core.ckeditor import html_converter
from tulius.forum import site
from tulius.forum import models
from tulius.forum import plugins
from tulius.forum import signals
from tulius.forum.threads import api
from tulius.forum.comments import pagination
from tulius.websockets import publisher


@dispatch.receiver(signals.thread_prepare_room)
def prepare_room_list(sender, room, threads, **kwargs):
    room.comments_count = 0
    room.last_comment_id = None
    for thread in threads:
        room.comments_count += thread.comments_count
        if (not room.last_comment_id) or (
                room.last_comment_id < thread.last_comment_id):
            room.last_comment_id = thread.last_comment_id


def comment_to_json(c):
    return {
        'id': c.id,
        'url': c.get_absolute_url,
        'title': html.escape(c.title),
        'body': bbcodes.bbcode(c.body),
        'user': api.user_to_json(c.user, detailed=True),
        'create_time': c.create_time,
        'voting': c.voting,
        'edit_right': c.edit_right,
        'is_thread': c.is_thread(),
        'edit_time': c.edit_time,
        'editor': api.user_to_json(c.editor) if c.editor else None
    }


class CommentsPageAPI(api.BaseThreadView):
    def get_context_data(self, **kwargs):
        super(CommentsPageAPI, self).get_context_data(**kwargs)
        page_num = int(kwargs['page_num'])
        comments = models.Comment.objects.select_related('user')
        comments = comments.filter(
            parent=self.obj, page=page_num).exclude(deleted=True)
        for comment in comments:
            comment.view_user = self.user
            comment.parent = self.obj
        pagination_context = pagination.get_pagination_context(
            self.request, page_num, self.obj.pages_count)
        return {
            'pagination': pagination_context,
            'comments': [comment_to_json(c) for c in comments]
        }

    @classmethod
    def as_view(cls, **initkwargs):
        view = super(CommentsPageAPI, cls).as_view(**initkwargs)
        return transaction.non_atomic_requests(view)

    def post(self, *args, **kwargs):
        transaction.set_autocommit(False)
        self.get_parent_thread(**kwargs)
        if not self.obj.write_right(self.user):
            raise exceptions.PermissionDenied()
        data = json.loads(self.request.body)
        text = html_converter.html_to_bb(data['body'])
        reply_id = data['reply_id']
        if reply_id != self.obj.first_comment_id:
            obj = shortcuts.get_object_or_404(models.Comment, pk=reply_id)
            if obj.parent_id != self.obj.id:
                raise exceptions.PermissionDenied()
        preview = data.get('preview', False)
        if text:
            comment = models.Comment(plugin_id=self.obj.plugin_id)
            comment.parent = self.obj
            comment.user = self.user
            comment.title = "Re: " + self.obj.title
            comment.body = text
            comment.reply_id = reply_id
            if preview:
                return comment_to_json(comment)
            comment.save()
            site.site.signals.comment_after_fastreply.send(self)
            # commit transaction to be sure that clients wouldn't be notified
            # before comment will be accessable in DB/
            transaction.commit()
            publisher.notify_thread_about_new_comment(
                self.obj.id, comment.id, comment.page)
            page = comment.page
        else:
            page = self.obj.pages_count
        return self.get_context_data(page_num=page, **kwargs)


class CommentAPI(plugins.BaseAPIView):
    obj = None

    def get_comment(self, **kwargs):
        core = site.site.core
        self.obj = core.get_parent_comment(self.user, kwargs['pk'], False)[1]

    def get_context_data(self, **kwargs):
        self.get_comment(**kwargs)
        return comment_to_json(self.obj)

    def delete(self, *args, **kwargs):
        self.get_comment(**kwargs)
        if self.obj.is_thread():
            raise models.Comment.DoesNotExist()
        site.site.core.delete_comment(
            self.user, self.obj.id, self.request.GET['comment'])
        thread = models.Thread.objects.get(pk=self.obj.parent.id)
        # TODO clients notification
        return {'pages_count': thread.pages_count}
