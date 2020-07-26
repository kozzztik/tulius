import json

from django import dispatch
from django import shortcuts
from django import urls
from django.core import exceptions
from django.db import transaction
from django.utils import html, timezone
from djfw.wysibb.templatetags import bbcodes

from tulius.core.ckeditor import html_converter
from tulius.forum.comments import models
from tulius.forum.threads import views
from tulius.forum.threads import models as thread_models
from tulius.forum.threads import signals as thread_signals
from tulius.forum.comments import pagination
from tulius.forum.comments import signals as comment_signals
from tulius.websockets import publisher


@dispatch.receiver(thread_signals.prepare_room)
def prepare_room_list(room, threads, **_kwargs):
    room.comments_count = 0
    room.last_comment_id = None
    for thread in threads:
        room.comments_count += thread.comments_count
        if (not room.last_comment_id) or (
                room.last_comment_id < thread.last_comment_id):
            room.last_comment_id = thread.last_comment_id


def order_to_page(order):
    return int(order / CommentsBase.COMMENTS_ON_PAGE) + 1


@dispatch.receiver(thread_signals.room_to_json, sender=thread_models.Thread)
def room_to_json(instance, response, view, **_kwargs):
    if instance.last_comment_id is None:
        return
    try:
        last_comment = models.Comment.objects.select_related('user').get(
            id=instance.last_comment_id)
    except models.Comment.DoesNotExist:
        return
    response['last_comment'] = {
        'id': last_comment.id,
        'thread': {
            'id': last_comment.parent_id,
            'url': view.thread_url(last_comment.parent_id)
        },
        'page': order_to_page(last_comment.order),
        'user': views.user_to_json(last_comment.user),
        'create_time': last_comment.create_time,
    }
    response['comments_count'] = instance.comments_count
    response['pages_count'] = CommentsBase.pages_count(instance)


class CommentsBase(views.BaseThreadView):
    COMMENTS_ON_PAGE = 25
    comment_model = models.Comment

    @classmethod
    def pages_count(cls, thread):
        return order_to_page(thread.comments_count - 1)

    @staticmethod
    def comment_url(comment):
        return urls.reverse('forum_api:comment', kwargs={'pk': comment.id})

    def comment_edit_right(self, comment):
        return (comment.user == self.user) or self.rights.moderate

    @classmethod
    def on_fix_counters(cls, sender, thread, view, **kwargs):
        if thread.room:
            return
        comments = cls.comment_model.objects.filter(
            parent=thread, deleted=False)
        thread.comments_count = 0
        thread.first_comment_id = None
        for comment in comments.order_by('id'):
            comment = cls.comment_model.objects.select_for_update(
                ).get(pk=comment.pk)
            comment.order = thread.comments_count
            comment.save()
            thread.comments_count += 1
            if not thread.first_comment_id:
                thread.first_comment_id = comment.pk
            thread.last_comment_id = comment.pk
        if getattr(view, 'result', None):
            view.result['comments'] = view.result.get(
                'comments', 0) + thread.comments_count

    def comment_to_json(self, c):
        data = {
            'id': c.id,
            'thread': {
                'id': c.parent_id,
                'url': self.thread_url(c.parent_id)
            },
            'page': order_to_page(c.order),
            'url': self.comment_url(c) if c.pk else None,
            'title': html.escape(c.title),
            'body': bbcodes.bbcode(c.body),
            'user': views.user_to_json(c.user, detailed=True),
            'create_time': c.create_time,
            'edit_right': self.comment_edit_right(c),
            'is_thread': c.is_thread(),
            'edit_time': c.edit_time,
            'editor': views.user_to_json(c.editor) if c.editor else None,
            'media': c.media,
            'reply_id': c.reply_id,
        }
        comment_signals.to_json.send(
            self.comment_model, comment=c, data=data, view=self)
        return data


class CommentsPageAPI(CommentsBase):
    def get_context_data(self, **kwargs):
        self.get_parent_thread(**kwargs)
        page_num = kwargs.get('page') or int(self.request.GET.get('page', 1))
        comments = self.comment_model.objects.select_related('user')
        comments = comments.exclude(deleted=True).filter(
            parent=self.obj,
            order__gte=CommentsBase.COMMENTS_ON_PAGE * (page_num - 1),
            order__lt=CommentsBase.COMMENTS_ON_PAGE * page_num
        )
        for comment in comments:
            # TODO remove it. needed only for c.is_thread() call
            comment.parent = self.obj
        # TODO move pagination to frontend
        pagination_context = pagination.get_pagination_context(
            self.request, page_num, self.pages_count(self.obj))
        return {
            'pagination': pagination_context,
            'comments': [self.comment_to_json(c) for c in comments]
        }

    @classmethod
    def on_create_thread(cls, instance, data, preview, view, **_kwargs):
        if not instance.room:
            cls.create_comment_process(data, preview, view)
            if not preview:
                instance.save()

    @classmethod
    def create_comment(cls, data, view):
        reply_id = data.get('reply_id') or view.obj.first_comment_id
        if reply_id and (reply_id != view.obj.first_comment_id):
            obj = shortcuts.get_object_or_404(cls.comment_model, pk=reply_id)
            if obj.parent_id != view.obj.id:
                raise exceptions.PermissionDenied()
        comment = cls.comment_model()
        comment.parent = view.obj
        comment.user = view.user
        comment.title = data['title']
        comment.body = data['body']
        comment.reply_id = reply_id
        comment.media = {}
        comment.order = view.obj.comments_count
        return comment

    @classmethod
    def create_comment_process(cls, data, preview, view):
        comment = cls.create_comment(data, view=view)
        comment_signals.before_add.send(
            cls.comment_model, comment=comment, data=data, preview=preview,
            view=view)
        if not preview:
            comment.save()
        view.obj.comments_count += 1
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
            page = order_to_page(comment.order)
            publisher.notify_thread_about_new_comment(
                self, self.obj, comment, page)
        else:
            page = self.pages_count(self.obj)
        return self.get_context_data(page=page, **kwargs)


thread_signals.after_create.connect(
    CommentsPageAPI.on_create_thread, sender=thread_models.Thread)


class CommentBase(CommentsBase):
    comment = None

    def get_comment(self, pk, for_update=False, **kwargs):
        query = self.comment_model.objects.filter(deleted=False)
        if for_update:
            query = query.select_for_update()
        self.comment = shortcuts.get_object_or_404(query, id=int(pk))
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
    def delete(self, request, **kwargs):
        self.get_comment(for_update=True, **kwargs)
        if self.comment.is_thread():
            raise exceptions.PermissionDenied()
        if not self.comment_edit_right(self.comment):
            raise exceptions.PermissionDenied()
        self.comment.deleted = True
        self.comment.data['deleted'] = {
            'user_id': self.user.pk,
            'time': timezone.now().isoformat(),
            'description': request.GET['comment'],
        }
        comment_signals.on_delete.send(
            self.comment_model, comment=self.comment, view=self)
        self.comment.save()
        # update page nums
        self.on_fix_counters(self.comment_model, self.obj, self)
        self.obj.save()
        # TODO clients notification
        return {'pages_count': self.pages_count(self.obj)}

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
    def on_thread_update(cls, instance, data, preview, view, **_kwargs):
        if not instance.room:
            comment = cls.comment_model.objects.select_for_update().get(
                id=instance.first_comment_id)
            cls.update_comment(comment, data, preview, view)
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


thread_signals.on_update.connect(
    CommentAPI.on_thread_update, sender=thread_models.Thread)
thread_signals.on_fix_counters.connect(
    CommentsPageAPI.on_fix_counters, sender=thread_models.Thread)
