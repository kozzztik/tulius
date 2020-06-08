from django import shortcuts
from django.db.models.query_utils import Q
from django.conf.urls import url
from django.utils import html
from django import urls

from tulius.stories import models as stories_models
# TODO: fix this when module moved
from tulius.forum.threads import views
from tulius.forum.threads import api
from tulius.forum.threads.plugin import ThreadsPlugin
from tulius.stories.models import Avatar, Role, AdditionalMaterial, \
    Illustration
from tulius.gameforum.models import Trustmark
from tulius.gameforum import consts
from tulius.gameforum import rights
from djfw.wysibb.templatetags import bbcodes


class GameThreadsPlugin(ThreadsPlugin):
    room_list_template = 'gameforum/snippets/room_list.haml'
    thread_list_template = 'gameforum/snippets/thread_list.haml'
    thread_edit_template = 'gameforum/add_post.haml'

    # pylint: disable=too-many-branches
    def get_parent_thread(self, user, thread_id, is_room=None):
        thread = super(GameThreadsPlugin, self).get_parent_thread(
            user, thread_id, is_room)
        variation = thread.variation
        thread.all_roles = Role.objects.filter(variation=variation)
        avatars = Avatar.objects.filter(
            id__in=[
                role.avatar_id for role in thread.all_roles if role.avatar_id])
        for role in thread.all_roles:
            role.my_trust = self.site.core.mark_to_percents(0)
            if role.avatar_id:
                for avatar in avatars:
                    if avatar.id == role.avatar_id:
                        role.avatar = avatar
                        break
        thread.edit_marks = variation.game and variation.game.write_right(user)
        if not user.is_anonymous:
            trustmarks = Trustmark.objects.filter(
                variation=variation, user=user)
            for mark in trustmarks:
                for role in thread.all_roles:
                    if mark.role_id == role.id:
                        role.my_trust = self.site.core.mark_to_percents(
                            mark.value)
                        break
        if thread.game:
            if thread.game.edit_right(user):
                thread.roles_list = [
                    role for role in thread.all_roles if not role.deleted]
            elif thread.game.status >= 5:
                thread.roles_list = [
                    role for role in thread.all_roles
                    if not role.deleted and role.show_in_character_list]
            else:
                thread.roles_list = [
                    role for role in thread.all_roles
                    if role.user_id == user.id]
        else:
            thread.roles_list = []
        thread.character_list = [
            role for role in thread.all_roles if not role.deleted]
        query_materials = Q(variation=thread.variation) | Q(
            story_id=thread.variation.story_id)
        if thread.game and (not thread.game.edit_right(user)):
            thread.character_list = [
                role for role in thread.character_list
                if role.show_in_character_list]
            query_materials = query_materials & Q(admins_only=False)
        thread.materials = AdditionalMaterial.objects.filter(query_materials)
        thread.illustrations = Illustration.objects.filter(query_materials)
        rolize_list = {}
        for role in thread.all_roles:
            rolize_list[role.id] = role
        thread.rolize_list = rolize_list
        return thread

    def rolize(self, posts, variation, roles_list):
        for post in posts:
            if post.data1:
                post.role = roles_list[post.data1] if (
                    post.data1 in roles_list) else None
            else:
                post.role = None
            if post.data2:
                post.edit_role = roles_list[post.data2] if (
                    post.data2 in roles_list) else None
            else:
                post.edit_role = None
        return posts

    def rolize_lastest(self, posts, variation, roles_list):
        for post in posts:
            if post.last_comment and post.last_comment.data1:
                post.last_comment.role = roles_list[
                    post.last_comment.data1] if (
                        post.last_comment.data1 in roles_list) else None
        return posts

    def rolize_comments(self, sender, **kwargs):
        comments = kwargs["comments"]
        self.rolize(comments, sender.variation, sender.rolize_list)

    def post_init(self):
        self.site.signals.read_comments.connect(self.rolize_comments)

    def move_list(self, thread, user):
        queryset = self.models.Thread.objects.filter(
            plugin_id=self.site_id, level=0, tree_id=thread.tree_id)
        return self.expand_move_list(queryset, thread, user)

    def get_urls(self):
        return [
            url(r'^$', views.Index.as_view(), name='index'),
            url(
                r'^(?P<variation_id>\d+)/',
                views.Index.as_view(), name='game_forum_variation'),
            url(
                r'^(?P<variation_id>\d+)/room/(?P<pk>\d+)/',
                views.Index.as_view(), name='room_new'),
            url(
                r'^(?P<variation_id>\d+)/thread/(?P<pk>\d+)/',
                views.Index.as_view(), name='thread_new'),
            url(
                r'^room/(?P<parent_id>\d+)/$',
                views.Index.as_view(), name='room'),
            url(
                r'^add_room/$',
                views.EditView.as_view(plugin=self, self_is_room=True),
                name='add_room'),
            url(
                r'^add_room/(?P<parent_id>\d+)/$',
                views.EditView.as_view(plugin=self, self_is_room=True),
                name='add_room'),
            url(
                r'^edit_room/(?P<thread_id>\d+)/$',
                views.EditView.as_view(plugin=self, self_is_room=True),
                name='edit_room'),
            url(
                r'^add_thread/(?P<parent_id>\d+)/$',
                views.EditView.as_view(plugin=self, self_is_room=False),
                name='add_thread'),
            url(
                r'^edit_thread/(?P<thread_id>\d+)/$',
                views.EditView.as_view(plugin=self, self_is_room=False),
                name='edit_thread'),
            url(
                r'^thread/(?P<parent_id>\d+)/$',
                views.Thread.as_view(plugin=self), name='thread'),
            url(
                r'^thread/(?P<parent_id>\d+)/move/$',
                views.MoveThreadSelect.as_view(plugin=self),
                name='thread_move'),
            url(
                r'^thread/(?P<parent_id>\d+)/move/(?P<thread_id>\d+)/$',
                views.MoveThreadConfirm.as_view(plugin=self),
                name='thread_move_confirm'),
            url(r'^thread/(?P<parent_id>\d+)/move/root/$',
                views.MoveThreadConfirm.as_view(plugin=self),
                name='thread_move_confirm'),
            url(
                r'^delete_thread/$',
                views.DeleteThread.as_view(plugin=self),
                name='delete_thread'),
        ]

# TODO forum actions trustmarks (also in char modal)
# TODO forum actions illustration lightbox
# TODO forum actions delete thread/room
# TODO search action
# TODO online status
# TODO rights superuser equal
# TODO cleanup not used items
# TODO threads page


class BaseThreadAPI(api.BaseThreadView):
    plugin_id = consts.GAME_FORUM_SITE_ID
    variation = None
    all_roles: dict = None

    def get_parent_thread(self, **kwargs):
        variation_id = kwargs['variation_id']
        self.variation = shortcuts.get_object_or_404(
            stories_models.Variation, pk=variation_id)
        super(BaseThreadAPI, self).get_parent_thread(**kwargs)
        roles = stories_models.Role.objects.filter(
            variation=self.variation)
        self.all_roles = {role.id: role for role in roles}

    def _get_rights_checker(self, thread, parent_rights=None):
        return rights.RightsChecker(
            self.variation, thread, self.user, parent_rights=parent_rights)

    def role_to_json(self, role_id):
        if role_id is None:
            return None
        role = self.all_roles[role_id]
        return {
            'id': role.id,
            'title': html.escape(role.name),
            'url': role.get_absolute_url(),
        }

    def thread_url(self, thread):
        return urls.reverse(
            'gameforum:room_new' if thread.room else 'gameforum:thread_new',
            kwargs={
                'variation_id': self.variation.id, 'pk': thread.id})

    def room_to_json(self, thread):
        return {
            'id': thread.pk,
            'title': html.escape(thread.title),
            'body': bbcodes.bbcode(thread.body),
            'room': thread.room,
            'deleted': thread.deleted,
            'important': thread.important,
            'closed': thread.closed,
            'user': self.role_to_json(thread.data1),
            'moderators': [
                self.role_to_json(user) for user in thread.moderators],
            'accessed_users': None if thread.accessed_users is None else [
                self.role_to_json(user) for user in thread.accessed_users
            ],
            'threads_count': thread.threads_count if thread.room else None,
            'comments_count': thread.comments_count,
            'pages_count': thread.pages_count,
            'url': self.thread_url(thread),
            'last_comment': {
                'url': thread.last_comment.get_absolute_url,
                'user': self.role_to_json(thread.last_comment.data1),
                'create_time': thread.last_comment.create_time,
            } if thread.last_comment else None,
            'unreaded':
                thread.unreaded.get_absolute_url if thread.unreaded else None,
        }


class ThreadAPI(api.ThreadView, BaseThreadAPI):
    pass
