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
        comment_signals.to_json.send(
            self.comment_model, comment=c, data=data, view=self)
        return data


class CommentsPageAPI(CommentsBase):
    COMMENTS_ON_PAGE = 25

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

    @classmethod
    def on_create_thread(cls, sender, thread, data, preview, **kwargs):
        if not thread.room:
            cls.create_comment_process(data, preview, sender)
            if not preview:
                thread.save()

    @classmethod
    def create_comment(cls, data, view):
        reply_id = data.get('reply_id') or view.obj.first_comment_id
        if reply_id and (reply_id != view.obj.first_comment_id):
            obj = shortcuts.get_object_or_404(cls.comment_model, pk=reply_id)
            if obj.parent_id != view.obj.id:
                raise exceptions.PermissionDenied()
        comment = cls.comment_model(plugin_id=view.obj.plugin_id)
        comment.parent = view.obj
        comment.user = view.user
        comment.title = data['title']
        comment.body = data['body']
        comment.reply_id = reply_id
        return comment

    @classmethod
    def create_comment_process(cls, data, preview, view):
        comment = cls.create_comment(data, view=view)
        comment.media = {}
        comment_signals.before_add.send(
            cls.comment_model, comment=comment, data=data, preview=preview,
            view=view)
        comments_count = cls.comment_model.objects.filter(
            parent=view.obj, deleted=False).count()
        comment.page = int(comments_count / cls.COMMENTS_ON_PAGE) + 1
        if not preview:
            comment.save()
        view.obj.comments_count = comments_count + 1
        if not view.obj.first_comment_id:
            view.obj.first_comment_id = comment.pk
        view.obj.last_comment_id = comment.pk
        results = comment_signals.after_add.send(
            cls.comment_model, comment=comment, data=data, preview=preview,
            view=view)
        if any(map(lambda a: a[1], results)):
            comment.save()
        return comment

    def post(self, request, **kwargs):
        transaction.set_autocommit(False)
        self.get_parent_thread(for_update=True, **kwargs)
        if not self.rights.write:
            raise exceptions.PermissionDenied()
        data = json.loads(request.body)
        data['body'] = html_converter.html_to_bb(data['body'])
        preview = data.pop('preview', False)
        if data['body']:
            comment = self.create_comment_process(data, preview, self)
            if preview:
                return self.comment_to_json(comment)
            # commit transaction to be sure that clients wouldn't be notified
            # before comment will be accessible in DB
            self.obj.save()
            transaction.commit()
            publisher.notify_thread_about_new_comment(self, self.obj, comment)
            page = comment.page
        else:
            page = self.obj.pages_count
        return self.get_context_data(page=page, **kwargs)


@dispatch.receiver(signals.after_create_thread)
def tmp_on_create_plugin_filter(
        sender, thread, data, preview, **kwargs):
    # TODO this func will be removed with plugin_id field cleanup
    # it will use signals "sender" field
    if thread.plugin_id:
        return None
    return CommentsPageAPI.on_create_thread(
        sender, thread, data, preview, **kwargs)


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

    @classmethod
    def update_comment(cls, comment, data, preview, view):
        comment.edit_time = timezone.now()
        comment.editor = view.request.user
        comment.title = data['title'][:120]
        comment.body = data['body']
        comment_signals.on_update.send(
            cls.comment_model, comment=comment, data=data,
            preview=preview, view=view)

    @classmethod
    def on_thread_update(cls, sender, thread, data, preview, **kwargs):
        if not thread.room:
            comment = cls.comment_model.objects.select_for_update().get(
                id=thread.first_comment_id)
            cls.update_comment(comment, data, preview, sender)
            if not preview:
                comment.save()

    def post(self, request, **kwargs):
        data = json.loads(request.body)
        data['body'] = html_converter.html_to_bb(data['body'])
        preview = data.pop('preview', False)
        transaction.set_autocommit(False)
        self.get_comment(for_update=True, **kwargs)
        if self.comment.is_thread():
            raise exceptions.PermissionDenied()
        if not self.comment_edit_right(self.comment):
            raise exceptions.PermissionDenied()

        self.update_comment(self.comment, data, preview, self)

        if preview:
            transaction.rollback()
        else:
            self.comment.save()
            transaction.commit()
        return self.comment_to_json(self.comment)


@dispatch.receiver(signals.update_thread)
def tmp_on_update_plugin_filter(
        sender, thread, data, preview, **kwargs):
    # TODO this func will be removed with plugin_id field cleanup
    # it will use signals "sender" field
    if thread.plugin_id:
        return None
    return CommentAPI.on_thread_update(
        sender, thread, data, preview, **kwargs)
