from django import dispatch
from django.core import exceptions
from django.db import models as dj_models

from tulius.forum.threads import signals as thread_signals
from tulius.forum.comments import signals as comment_signals
from tulius.stories import models as stories_models
from tulius.gameforum.threads import models as thread_models
from tulius.gameforum.threads import views as threads
from tulius.gameforum.comments import models as comment_models
from tulius.forum.comments import views as comments
from tulius.forum.comments import mutations
from tulius.forum.threads import mutations as base_mutations
from tulius.gameforum.rights import mutations as rights_mutations


base_mutations.on_mutation(rights_mutations.UpdateRights)(
    mutations.FixCountersOnRights)


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
def before_create_thread(instance, data, **_kwargs):
    if instance.room:
        return
    images_data = data['media'].get('illustrations')
    if not images_data:
        return
    instance.media['illustrations'] = validate_image_data(
        instance.variation, images_data)


@dispatch.receiver(comment_signals.before_add, sender=comment_models.Comment)
def before_add_comment(comment, data, **_kwargs):
    images_data = data['media'].get('illustrations')
    if not images_data:
        return
    if comment.is_thread():
        comment.media['illustrations'] = comment.parent.media['illustrations']
    else:
        comment.media['illustrations'] = validate_image_data(
            comment.parent.variation, images_data)


@dispatch.receiver(comment_signals.on_update, sender=comment_models.Comment)
def on_comment_update(comment, data, **_kwargs):
    images_data = data['media'].get('illustrations')
    orig_data = comment.media.get('illustrations')
    if images_data:
        images_data = validate_image_data(
            comment.parent.variation, images_data)
    if orig_data and not images_data:
        del comment.media['illustrations']
    elif images_data:
        comment.media['illustrations'] = images_data
    if comment.is_thread():
        if (not images_data) and ('illustrations' in comment.parent.media):
            del comment.parent.media['illustrations']
        elif images_data:
            comment.parent.media['illustrations'] = images_data


@dispatch.receiver(thread_signals.to_json_as_item, sender=thread_models.Thread)
def thread_item_to_json(instance, response, user, **_kwargs):
    last_comment_id = instance.last_comment[user]
    comments_count = instance.comments_count[user]
    response['comments_count'] = comments_count
    if (not instance.room) and (comments_count is not None):
        response['pages_count'] = comment_models.Comment.order_to_page(
            comments_count - 1)
    if last_comment_id is None:
        return
    last_comment = comment_models.Comment.objects.filter(
        id=last_comment_id).first()
    if last_comment:
        response['last_comment'] = last_comment.to_json(user)


@dispatch.receiver(
    comment_signals.on_thread_delete, sender=thread_models.Thread)
def on_thread_delete(instance, **_kwargs):
    counts = instance.comments.filter(deleted=False).values(
        'role_id').annotate(count=dj_models.Count('role_id')).order_by('id')
    for item in counts:
        update_role_comments_count(item['role_id'], -item['count'])


class CommentsBase(threads.BaseThreadAPI, comments.CommentsBase):
    comment_model = comment_models.Comment

    def comments_query(self):
        # use reverse manager, so "parent" is cached correctly
        # no use of related user
        return self.obj.comments.exclude(deleted=True)


def update_role_comments_count(role_id, value):
    if role_id:
        stories_models.Role.objects.filter(pk=role_id).update(
            comments_count=dj_models.F('comments_count') + value)


class CommentsPageAPI(comments.CommentsPageAPI, CommentsBase):
    @classmethod
    def create_comment(cls, thread, user, data):
        comment = super().create_comment(thread, user, data)
        comment.role_id = cls.process_role(thread, user, None, data)
        update_role_comments_count(comment.role_id, 1)
        thread.variation.comments_count_inc(1)
        return comment


thread_signals.after_create.connect(
    CommentsPageAPI.on_create_thread, sender=thread_models.Thread)


@dispatch.receiver(comment_signals.on_delete, sender=comment_models.Comment)
def on_delete(comment, **_kwargs):
    update_role_comments_count(comment.role_id, -1)
    comment.parent.variation.comments_count_inc(-1)


class CommentAPI(comments.CommentAPI, CommentsBase):
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['thread']['rights'] = self.obj.rights_to_json(self.user)
        self.obj.rights_strict_roles(data['thread'], user=self.user)
        return data

    @classmethod
    def update_comment(cls, comment, user, data, preview):
        super().update_comment(comment, user, data, preview)
        new_role = data['role_id']
        if comment.role_id != new_role:
            if new_role not in comment.parent.write_roles(user):
                raise exceptions.PermissionDenied()
            update_role_comments_count(new_role, 1)
            update_role_comments_count(comment.role_id, -1)
            comment.role_id = new_role
        editor_role = data['edit_role_id']
        if editor_role not in comment.parent.write_roles(user):
            raise exceptions.PermissionDenied()
        comment.edit_role_id = editor_role


thread_signals.on_update.connect(
    CommentAPI.on_thread_update, sender=thread_models.Thread)
