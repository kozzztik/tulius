from django import dispatch
from django.core import exceptions
from django.db import models as dj_models
from django.utils import html
from djfw.wysibb.templatetags import bbcodes

from tulius.forum.threads import signals as thread_signals
from tulius.forum.comments import signals as comment_signals
from tulius.stories import models as stories_models
from tulius.gameforum.threads import models as thread_models
from tulius.gameforum.threads import views as threads
from tulius.gameforum.comments import models as comment_models
from tulius.forum.comments import views as comments


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


@dispatch.receiver(thread_signals.before_create, sender=thread_models.Thread)
def before_create_thread(instance, data, view, **_kwargs):
    if instance.room:
        return
    images_data = data['media'].get('illustrations')
    if not images_data:
        return
    instance.media['illustrations'] = validate_image_data(
        view.variation, images_data)


@dispatch.receiver(comment_signals.before_add, sender=comment_models.Comment)
def before_add_comment(comment, data, view, **_kwargs):
    images_data = data['media'].get('illustrations')
    if not images_data:
        return
    if comment.is_thread():
        comment.media['illustrations'] = view.obj.media['illustrations']
    else:
        comment.media['illustrations'] = validate_image_data(
            view.variation, images_data)


@dispatch.receiver(comment_signals.on_update, sender=comment_models.Comment)
def on_comment_update(comment, data, view, **_kwargs):
    images_data = data['media'].get('illustrations')
    orig_data = comment.media.get('illustrations')
    if images_data:
        images_data = validate_image_data(view.variation, images_data)
    if orig_data and not images_data:
        del comment.media['illustrations']
    elif images_data:
        comment.media['illustrations'] = images_data
    if comment.is_thread():
        if (not images_data) and ('illustrations' in view.obj.media):
            del view.obj.media['illustrations']
        elif images_data:
            view.obj.media['illustrations'] = images_data


@dispatch.receiver(thread_signals.room_to_json, sender=thread_models.Thread)
def room_to_json(instance, response, view, **_kwargs):
    last_comment_id = comment_models.get_param(
        'last_comment', instance, view.user.pk)
    comments_count = comment_models.get_param(
        'comments_count', instance, view.user.pk)
    response['comments_count'] = comments_count
    if not instance.room:
        response['pages_count'] = comments.order_to_page(comments_count - 1)
    if last_comment_id is None:
        return
    try:
        last_comment = comment_models.Comment.objects.select_related(
            'user').get(id=last_comment_id)
    except comment_models.Comment.DoesNotExist:
        return
    response['last_comment'] = {
        'id': last_comment.id,
        'thread': {
            'id': last_comment.parent_id,
        },
        'page': comments.order_to_page(last_comment.order),
        'user': view.role_to_json(last_comment.role_id),
        'create_time': last_comment.create_time,
    }


@dispatch.receiver(
    comment_signals.on_thread_delete, sender=thread_models.Thread)
def on_thread_delete(instance, **_kwargs):
    counts = instance.comments.filter(deleted=False).values(
        'role_id').annotate(count=dj_models.Count('role_id')).order_by('id')
    for item in counts:
        update_role_comments_count(item['role_id'], -item['count'])


class CommentsBase(threads.BaseThreadAPI, comments.CommentsBase):
    comment_model = comment_models.Comment

    def comment_to_json(self, c):
        data = {
            'id': c.id,
            'thread': {
                'id': c.parent_id,
                'url': c.parent.get_absolute_url(),
            },
            'page': comments.order_to_page(c.order),
            'url': c.get_absolute_url() if c.id else None,
            'title': html.escape(c.title),
            'body': bbcodes.bbcode(c.body),
            'user': self.role_to_json(c.role_id, detailed=True),
            'create_time': c.create_time,
            'edit_right': self.comment_edit_right(c),
            'is_thread': c.is_thread(),
            'edit_time': c.edit_time,
            'editor': self.role_to_json(c.edit_role_id) if c.editor else None,
            'media': c.media,
            'reply_id': c.reply_id,

        }
        comment_signals.to_json.send(
            self.comment_model, comment=c, data=data, view=self)
        return data


def update_role_comments_count(role_id, value):
    if role_id:
        stories_models.Role.objects.filter(pk=role_id).update(
            comments_count=dj_models.F('comments_count') + value)


class CommentsPageAPI(comments.CommentsPageAPI, CommentsBase):
    @classmethod
    def create_comment(cls, data, view):
        comment = super(CommentsPageAPI, cls).create_comment(data, view)
        comment.role_id = view.process_role(None, data)
        update_role_comments_count(comment.role_id, 1)
        view.variation.comments_count_inc(1)
        return comment


thread_signals.after_create.connect(
    CommentsPageAPI.on_create_thread, sender=thread_models.Thread)


@dispatch.receiver(comment_signals.on_delete, sender=comment_models.Comment)
def on_delete(comment, view, **_kwargs):
    update_role_comments_count(comment.role_id, -1)
    view.variation.comments_count_inc(-1)


class CommentAPI(comments.CommentAPI, CommentsBase):
    def get_context_data(self, **kwargs):
        data = super(CommentAPI, self).get_context_data(**kwargs)
        data['thread']['rights'] = self.obj.rights_to_json(self.user)
        return data

    @classmethod
    def update_comment(cls, comment, data, preview, view):
        super(CommentAPI, cls).update_comment(comment, data, preview, view)
        new_role = data['role_id']
        if comment.role_id != new_role:
            if new_role not in view.write_roles():
                raise exceptions.PermissionDenied()
            update_role_comments_count(new_role, 1)
            update_role_comments_count(comment.role_id, -1)
            comment.role_id = new_role
        editor_role = data['edit_role_id']
        if editor_role not in view.write_roles():
            raise exceptions.PermissionDenied()
        comment.edit_role_id = editor_role


thread_signals.on_update.connect(
    CommentAPI.on_thread_update, sender=thread_models.Thread)
