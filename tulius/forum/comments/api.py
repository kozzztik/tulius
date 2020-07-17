import json

from django import dispatch
from django import shortcuts
from django import urls
from django.core import exceptions
from django.db import transaction
from django.utils import html, timezone
from djfw.wysibb.templatetags import bbcodes

from tulius.core.ckeditor import html_converter
from tulius.forum import models
from tulius.forum import signals
from tulius.forum.threads import api
from tulius.forum.comments import pagination
from tulius.forum.comments import signals as comment_signals
from tulius.websockets import publisher


@dispatch.receiver(signals.after_create_thread)
def after_create_thread(sender, thread, data, preview, **kwargs):
    if thread.room:
        return
    comment = models.Comment(
        parent=thread, title=thread.title, body=thread.body,
        user=thread.user, plugin_id=thread.plugin_id)
    signals.before_add_comment.send(
        sender, comment=comment, data=data, preview=preview)
    if not preview:
        comment.save()
        thread.first_comment_id = comment.pk
        thread.last_comment_id = comment.pk
        thread.save()
    signals.after_add_comment.send(
        sender, comment=comment, data=data, preview=preview)


@dispatch.receiver(signals.update_thread)
def update_thread(sender, thread, data, preview, **kwargs):
    if thread.room:
        return
    comment = models.Comment.objects.get(id=thread.first_comment_id)
    comment.title = thread.title
    comment.body = thread.body
    comment.edit_time = timezone.now()
    comment.editor = sender.user
    signals.on_comment_update.send(
        sender, comment=comment, data=data, preview=preview)
    if not preview:
        comment.save()


@dispatch.receiver(signals.thread_prepare_room)
def prepare_room_list(sender, room, threads, **kwargs):
    room.comments_count = 0
    room.last_comment_id = None
    for thread in threads:
        room.comments_count += thread.comments_count
        if (not room.last_comment_id) or (
                room.last_comment_id < thread.last_comment_id):
            room.last_comment_id = thread.last_comment_id


@dispatch.receiver(signals.thread_room_to_json)
def room_to_json(sender, thread, response, **kwargs):
    if thread.plugin_id is not None:
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
        'user': api.user_to_json(last_comment.user),
        'create_time': last_comment.create_time,
    }


class CommentsBase(api.BaseThreadView):
    comment_model = models.Comment

    @staticmethod
    def comment_url(comment):
        return urls.reverse('forum_api:comment', kwargs={'pk': comment.id})

    def comment_edit_right(self, comment):
        return (comment.user == self.user) or self.rights.moderate

    def comment_to_json(self, c):
        data = {
            'id': c.id,
            'thread': {
                'id': c.parent_id,
                'url': self.thread_url(c.parent_id)
            },
            'page': c.page,
            'url': self.comment_url(c) if c.pk else None,
            'title': html.escape(c.title),
            'body': bbcodes.bbcode(c.body),
            'user': api.user_to_json(c.user, detailed=True),
            'create_time': c.create_time,
            'edit_right': self.comment_edit_right(c),
            'is_thread': c.is_thread(),
            'edit_time': c.edit_time,
            'editor': api.user_to_json(c.editor) if c.editor else None,
            'media': c.media,
            'reply_id': c.reply_id,
        }
        signals.comment_to_json.send(self, comment=c, data=data)
        return data


class CommentsPageAPI(CommentsBase):
    def get_context_data(self, **kwargs):
        self.get_parent_thread(**kwargs)
        page_num = kwargs.get('page') or int(self.request.GET.get('page', 1))
        comments = models.Comment.objects.select_related('user')
        comments = comments.filter(
            parent=self.obj, page=page_num).exclude(deleted=True)
        for comment in comments:
            # TODO remove it. needed only for c.is_thread() call
            comment.parent = self.obj
        # TODO move pagination to frontend
        pagination_context = pagination.get_pagination_context(
            self.request, page_num, self.obj.pages_count)
        return {
            'pagination': pagination_context,
            'comments': [self.comment_to_json(c) for c in comments]
        }

    def create_comment(self, text, data):
        reply_id = data['reply_id']
        if reply_id != self.obj.first_comment_id:
            obj = shortcuts.get_object_or_404(models.Comment, pk=reply_id)
            if obj.parent_id != self.obj.id:
                raise exceptions.PermissionDenied()
        comment = models.Comment(plugin_id=self.obj.plugin_id)
        comment.parent = self.obj
        comment.user = self.user
        comment.title = data['title']
        comment.body = text
        comment.reply_id = reply_id
        return comment

    def post(self, request, **kwargs):
        transaction.set_autocommit(False)
        self.get_parent_thread(**kwargs)
        if not self.rights.write:
            raise exceptions.PermissionDenied()
        data = json.loads(request.body)
        text = html_converter.html_to_bb(data.pop('body'))
        preview = data.pop('preview', False)
        if text:
            comment = self.create_comment(text, data)
            comment.media = {}
            signals.before_add_comment.send(
                self, comment=comment, data=data, preview=preview)
            if not preview:
                comment.save()
            signals.after_add_comment.send(
                self, comment=comment, data=data, preview=preview)
            if preview:
                return self.comment_to_json(comment)
            # commit transaction to be sure that clients wouldn't be notified
            # before comment will be accessible in DB
            transaction.commit()
            publisher.notify_thread_about_new_comment(self, self.obj, comment)
            page = comment.page
        else:
            page = self.obj.pages_count
        return self.get_context_data(page=page, **kwargs)


class CommentBase(CommentsBase):
    comment = None

    def get_comment(self, pk, for_update=False, **kwargs):
        query = models.Comment.objects.filter(deleted=False)
        if for_update:
            query = query.select_for_update()
        self.comment = shortcuts.get_object_or_404(
            query, id=int(pk), plugin_id=self.plugin_id)
        self.get_parent_thread(
            pk=self.comment.parent_id, for_update=for_update, **kwargs)


class CommentAPI(CommentBase):
    def get_context_data(self, **kwargs):
        self.get_comment(**kwargs)
        data = self.comment_to_json(self.comment)
        data['thread']['title'] = self.obj.title
        data['thread']['parents'] = [{
            'id': parent.id,
            'title': parent.title,
            'url': self.thread_url(parent.pk),
        } for parent in self.obj.get_ancestors()]
        return data

    @transaction.atomic
    def delete(self, *args, **kwargs):
        self.get_comment(for_update=True, **kwargs)
        if self.comment.is_thread():
            raise exceptions.PermissionDenied()
        if not self.comment_edit_right(self.comment):
            raise exceptions.PermissionDenied()
        self.comment.deleted = True
        delete_mark = models.CommentDeleteMark(
            comment=self.comment,
            user=self.user,
            description=self.request.GET['comment'])
        comment_signals.on_delete.send(
            self.comment_model, comment=self.comment, view=self)
        self.comment.save()
        delete_mark.save()
        # TODO clients notification
        return {'pages_count': self.obj.pages_count}

    def update_comment(self, comment, data):
        comment.edit_time = timezone.now()
        comment.editor = self.request.user
        comment.title = data['title'][:120]
        comment.body = html_converter.html_to_bb(data['body'])

    def post(self, request, **kwargs):
        data = json.loads(request.body)
        preview = data.pop('preview', False)
        transaction.set_autocommit(False)
        self.get_comment(for_update=True, **kwargs)
        if self.comment.is_thread():
            raise exceptions.PermissionDenied()
        if not self.comment_edit_right(self.comment):
            raise exceptions.PermissionDenied()

        self.update_comment(self.comment, data)

        signals.on_comment_update.send(
            self, comment=self.comment, data=data, preview=preview)
        if preview:
            transaction.rollback()
        else:
            self.comment.save()
            transaction.commit()
        return self.comment_to_json(self.comment)
