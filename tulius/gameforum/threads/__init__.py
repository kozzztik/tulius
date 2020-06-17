from django.db.models.query_utils import Q
from django.conf.urls import url

from tulius.forum.threads import views
from tulius.forum.threads.plugin import ThreadsPlugin
from tulius.stories.models import Role, AdditionalMaterial, \
    Illustration


class GameThreadsPlugin(ThreadsPlugin):
    thread_edit_template = 'gameforum/add_post.haml'

    # pylint: disable=too-many-branches
    def get_parent_thread(self, user, thread_id, is_room=None):
        thread = super(GameThreadsPlugin, self).get_parent_thread(
            user, thread_id, is_room)
        variation = thread.variation
        thread.all_roles = Role.objects.filter(variation=variation)
        thread.edit_marks = variation.game and variation.game.write_right(user)
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
                views.Index.as_view(), name='thread'),
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
        ]
