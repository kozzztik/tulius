import json

from django import dispatch
from django import shortcuts
from django.core import exceptions
from django.db import transaction
from django.utils import timezone

from tulius.core.ckeditor import html_converter
from tulius.forum.comments import models
from tulius.forum.threads import views
from tulius.forum.threads import models as thread_models
from tulius.forum.threads import signals as thread_signals
from tulius.forum.comments import pagination
from tulius.forum.comments import signals as comment_signals
from tulius.forum.comments import mutations
from tulius.websockets import publisher


@dispatch.receiver(thread_signals.to_json_as_item, sender=thread_models.Thread)
def thread_item_to_json(instance, response, user, **_kwargs):
    last_comment_id = instance.last_comment[user]
    comments_count = instance.comments_count[user]
    response['comments_count'] = comments_count
    if (not instance.room) and (comments_count is not None):
        response['pages_count'] = models.Comment.order_to_page(
            comments_count - 1)
    if last_comment_id is None:
        return
    last_comment = models.Comment.objects.select_related('user').filter(
        id=last_comment_id).first()
    if last_comment:
        response['last_comment'] = last_comment.to_json(user)


@dispatch.receiver(thread_signals.to_json)
def thread_to_json(instance, response, view, **_kwargs):
    response['first_comment_id'] = instance.first_comment[view.user]


class CommentsBase(views.BaseThreadView):
    comment_model = models.Comment

    @classmethod
    def pages_count(cls, thread):
        return cls.comment_model.order_to_page(thread.comments_count.su - 1)

    def comments_query(self):
        # use reverse manager, so "parent" is cached correctly
        return self.obj.comments.select_related('user').exclude(deleted=True)


class CommentsPageAPI(CommentsBase):
    def get_context_data(self, **kwargs):
        self.get_parent_thread(**kwargs)
        page_num = kwargs.get('page') or int(self.request.GET.get('page', 1))
        comments = self.comments_query().filter(
            order__gte=self.comment_model.COMMENTS_ON_PAGE * (page_num - 1),
            order__lt=self.comment_model.COMMENTS_ON_PAGE * page_num
        )
        # TODO move pagination to frontend
        pagination_context = pagination.get_pagination_context(
            self.request, page_num, self.pages_count(self.obj))
        return {
            'pagination': pagination_context,
            'comments': [c.to_json(self.user, detailed=True) for c in comments]
        }

    @classmethod
    def on_create_thread(cls, instance, data, preview, view, **_kwargs):
        if not instance.room:
            cls.create_comment_process(data, preview, view)
            if not preview:
                instance.save()

    @classmethod
    def create_comment(cls, data, view):
        reply_id = data.get('reply_id')
        if reply_id and (reply_id != view.obj.first_comment[view.user]):
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
        comment.order = view.obj.comments_count.su
        return comment

    @classmethod
    def create_comment_process(cls, data, preview, view):
        comment = cls.create_comment(data, view=view)
        comment_signals.before_add.send(
            cls.comment_model, comment=comment, data=data, preview=preview,
            view=view)
        if not preview:
            comment.save()
            mutations.ThreadCommentAdd(view.obj, comment).apply()
        results = comment_signals.after_add.send(
            cls.comment_model, comment=comment, data=data, preview=preview,
            view=view)
        if any(map(lambda a: a[1], results)):
            comment.save()
        return comment

    def post(self, request, **kwargs):
        transaction.set_autocommit(False)
        self.get_parent_thread(for_update=True, **kwargs)
        if not self.obj.write_right(self.user):
            raise exceptions.PermissionDenied()
        data = json.loads(request.body)
        data['body'] = html_converter.html_to_bb(data['body'])
        preview = data.pop('preview', False)
        if data['body']:
            comment = self.create_comment_process(data, preview, self)
            if preview:
                return comment.to_json(self.user, detailed=True)
            # commit transaction to be sure that clients wouldn't be notified
            # before comment will be accessible in DB
            self.obj.save()
            transaction.commit()
            page = comment.page
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
        self.comment.parent = self.obj  # for speedup


class CommentAPI(CommentBase):
    def get_context_data(self, **kwargs):
        self.get_comment(**kwargs)
        data = self.comment.to_json(self.user, detailed=True)
        data['thread']['title'] = self.obj.title
        data['thread']['parents'] = [{
            'id': parent.id,
            'title': parent.title,
            'url': parent.get_absolute_url(),
        } for parent in self.obj.get_parents()]
        return data

    @transaction.atomic
    def delete(self, request, **kwargs):
        self.get_comment(for_update=True, **kwargs)
        if self.comment.is_thread():
            raise exceptions.PermissionDenied()
        if not self.comment.edit_right(self.user):
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
        mutations.FixCounters(self.obj).apply()
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
                id=instance.first_comment[view.user])
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
        if not self.comment.edit_right(self.user):
            raise exceptions.PermissionDenied()

        self.update_comment(self.comment, data, preview, self)

        if preview:
            transaction.rollback()
        else:
            self.comment.save()
            transaction.commit()
        return self.comment.to_json(self.user, detailed=True)


thread_signals.on_update.connect(
    CommentAPI.on_thread_update, sender=thread_models.Thread)
