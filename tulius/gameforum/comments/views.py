from django import dispatch
from django import urls
from django.core import exceptions
from django.db import models as dj_models
from django.utils import html
from djfw.wysibb.templatetags import bbcodes

from tulius.forum import models
from tulius.forum.threads import signals as thread_signals
from tulius.forum.comments import signals as comment_signals
from tulius.stories import models as stories_models
from tulius.gameforum import consts
from tulius.gameforum.threads import views as threads
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


@dispatch.receiver(thread_signals.before_create)
def before_create_thread(instance, data, view, **_kwargs):
    if view.plugin_id != consts.GAME_FORUM_SITE_ID:
        return
    images_data = data['media'].get('illustrations')
    if not images_data:
        return
    instance.media['illustrations'] = validate_image_data(
        view.variation, images_data)


@dispatch.receiver(comment_signals.before_add)
def before_add_comment(comment, data, view, **_kwargs):
    if view.plugin_id != consts.GAME_FORUM_SITE_ID:
        return
    images_data = data['media'].get('illustrations')
    if not images_data:
        return
    if view.obj.first_comment_id == comment.id:
        comment.media['illustrations'] = view.obj.media['illustrations']
    else:
        comment.media['illustrations'] = validate_image_data(
            view.variation, images_data)


@dispatch.receiver(comment_signals.on_update)
def on_comment_update(comment, data, view, **_kwargs):
    if view.plugin_id != consts.GAME_FORUM_SITE_ID:
        return
    images_data = data['media'].get('illustrations')
    orig_data = comment.media.get('illustrations')
    if images_data:
        images_data = validate_image_data(view.variation, images_data)
    if orig_data and not images_data:
        del comment.media['illustrations']
    elif images_data:
        comment.media['illustrations'] = images_data
    if view.obj.first_comment_id == comment.id:
        if (not images_data) and ('illustrations' in view.obj.media):
            del view.obj.media['illustrations']
        elif images_data:
            view.obj.media['illustrations'] = images_data


@dispatch.receiver(thread_signals.room_to_json)
def room_to_json(instance, response, view, **_kwargs):
    if instance.plugin_id != consts.GAME_FORUM_SITE_ID:
        return
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
        'page': last_comment.page,
        'user': view.role_to_json(last_comment.data1),
        'create_time': last_comment.create_time,
    }
    response['comments_count'] = instance.comments_count
    response['pages_count'] = CommentsBase.pages_count(instance)


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
        comment_signals.to_json.send(
            self.comment_model, comment=c, data=data, view=self)
        return data

    @classmethod
    def on_fix_counters(cls, sender, thread, view, **kwargs):
        if (thread.plugin_id != consts.GAME_FORUM_SITE_ID) or thread.parent_id:
            return None
        variation = stories_models.Variation.objects.select_for_update(
            ).get(thread=thread)
        roles = stories_models.Role.objects.filter(variation=variation)
        for role in roles:
            role = stories_models.Role.objects.select_for_update(
                ).get(pk=role.pk)
            role.comments_count = cls.comment_model.objects.filter(
                parent__tree_id=thread.tree_id, deleted=False,
                data1=role.id).count()
            role.save()
        variation.comments_count = cls.comment_model.objects.filter(
            parent__tree_id=thread.tree_id, deleted=False).count()
        variation.save()
        return None


dispatch.receiver(thread_signals.on_fix_counters)(CommentsBase.on_fix_counters)


def update_role_comments_count(role_id, value):
    if role_id:
        stories_models.Role.objects.filter(pk=role_id).update(
            comments_count=dj_models.F('comments_count') + value)


class CommentsPageAPI(comments.CommentsPageAPI, CommentsBase):
    @classmethod
    def create_comment(cls, data, view):
        comment = super(CommentsPageAPI, cls).create_comment(data, view)
        comment.data1 = view.process_role(None, data)
        update_role_comments_count(comment.data1, 1)
        view.variation.comments_count_inc(1)
        return comment

    @classmethod
    def on_create_thread(cls, instance, data, preview, view, **kwargs):
        # TODO this func will be removed with plugin_id field cleanup
        # it will use signals "sender" field
        if instance.plugin_id != consts.GAME_FORUM_SITE_ID:
            return
        super(CommentsPageAPI, cls).on_create_thread(
            instance, data, preview, view, **kwargs)


dispatch.receiver(thread_signals.after_create)(
    CommentsPageAPI.on_create_thread)


@dispatch.receiver(comment_signals.on_delete)
def on_delete(sender, comment, view, **kwargs):
    if comment.plugin_id == consts.GAME_FORUM_SITE_ID:
        update_role_comments_count(comment.data1, -1)
        view.variation.comments_count_inc(-1)


class CommentAPI(comments.CommentAPI, CommentsBase):
    def get_context_data(self, **kwargs):
        data = super(CommentAPI, self).get_context_data(**kwargs)
        data['thread']['rights'] = self.rights.to_json()
        return data

    @classmethod
    def update_comment(cls, comment, data, preview, view):
        super(CommentAPI, cls).update_comment(comment, data, preview, view)
        new_role = data['role_id']
        if comment.data1 != new_role:
            if new_role not in view.rights.user_write_roles:
                raise exceptions.PermissionDenied()
            update_role_comments_count(new_role, 1)
            update_role_comments_count(comment.data1, -1)
            comment.data1 = new_role
        editor_role = data['edit_role_id']
        if editor_role not in view.rights.user_write_roles:
            raise exceptions.PermissionDenied()
        comment.data2 = editor_role

    @classmethod
    def on_thread_update(cls, instance, data, preview, view, **kwargs):
        # TODO this func will be removed with plugin_id field cleanup
        # it will use signals "sender" field
        if instance.plugin_id == consts.GAME_FORUM_SITE_ID:
            super(CommentAPI, cls).on_thread_update(
                instance, data, preview, view, **kwargs)


dispatch.receiver(thread_signals.on_update)(CommentAPI.on_thread_update)


@dispatch.receiver(thread_signals.on_fix_counters)
def tmp_on_fix_plugin_filter(sender, thread, view, **kwargs):
    # TODO this func will be removed with plugin_id field cleanup
    # it will use signals "sender" field
    if thread.plugin_id != consts.GAME_FORUM_SITE_ID:
        return None
    return CommentsPageAPI.on_fix_counters(sender, thread, view, **kwargs)
