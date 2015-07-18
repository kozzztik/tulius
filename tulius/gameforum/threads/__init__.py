from django.conf.urls import patterns, url
from django.db.models.query_utils import Q
# TODO: fix this when module moved
from tulius.forum import ThreadsPlugin
from tulius.stories.models import Avatar, Role, Variation, AdditionalMaterial, Illustration
from tulius.gameforum.models import Trustmark
from tulius.games.models import GAME_STATUS_FINISHING, GAME_STATUS_COMPLETED 

class GameThreadsPlugin(ThreadsPlugin):
    room_list_template = 'gameforum/snippets/room_list.haml'
    thread_list_template = 'gameforum/snippets/thread_list.haml'
    thread_edit_template = 'gameforum/add_post.haml'
    
    def get_parent_thread(self, user, thread_id, is_room=None):
        thread = super(GameThreadsPlugin, self).get_parent_thread(user, thread_id, is_room)
        variation = thread.variation
        thread.all_roles = Role.objects.filter(variation=variation)
        avatars = Avatar.objects.filter(id__in=[role.avatar_id for role in thread.all_roles if role.avatar_id])
        for role in thread.all_roles:
            role.my_trust = self.site.core.mark_to_percents(0)
            if role.avatar_id:
                for avatar in avatars:
                    if avatar.id == role.avatar_id:
                        role.avatar = avatar
                        break
        thread.edit_marks = variation.game and variation.game.write_right(user)
        if not user.is_anonymous():
            trustmarks = Trustmark.objects.filter(variation=variation, user=user)
            for mark in trustmarks:
                for role in thread.all_roles:
                    if mark.role_id == role.id:
                        role.my_trust = self.site.core.mark_to_percents(mark.value)
                        break
        if thread.game:
            if thread.game.edit_right(user): 
                thread.roles_list = [role for role in thread.all_roles if not role.deleted]
            elif thread.game.status >= 5:
                thread.roles_list = [role for role in thread.all_roles if not role.deleted and role.show_in_character_list]    
            else:
                thread.roles_list = [role for role in thread.all_roles if (role.user_id == user.id)]
        else:
            thread.roles_list = []
        thread.character_list =  [role for role in thread.all_roles if not role.deleted]
        query_materials = Q(variation=thread.variation) | Q(story_id=thread.variation.story_id)
        if thread.game and (not thread.game.edit_right(user)):
            thread.character_list = [role for role in thread.character_list if role.show_in_character_list] 
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
                post.role = roles_list[post.data1] if (post.data1 in roles_list) else None
            else:
                post.role = None
            if post.data2:
                post.edit_role = roles_list[post.data2] if (post.data2 in roles_list) else None
            else:
                post.edit_role = None
        return posts
    
    def rolize_lastest(self, posts, variation, roles_list):
        for post in posts:
            if post.last_comment and post.last_comment.data1:
                post.last_comment.role = roles_list[post.last_comment.data1] if (post.last_comment.data1 in roles_list) else None
        return posts
    
    def get_subthreads(self, user, parent_thread, is_room=False):
        threads = super(GameThreadsPlugin, self).get_subthreads(user, parent_thread, is_room)
        threads = self.rolize(threads, parent_thread.variation, parent_thread.rolize_list)
        threads = self.rolize_lastest(threads, parent_thread.variation, parent_thread.rolize_list)
        return threads
    
    def rolize_comments(self, sender, **kwargs):
        comments = kwargs["comments"]
        comments = self.rolize(comments, sender.variation, sender.rolize_list)
    
    def post_init(self):
        self.site.signals.read_comments.connect(self.rolize_comments)
        
    def move_list(self, thread, user):
        queryset = self.models.Thread.objects.filter(plugin_id=self.site_id, level=0, tree_id=thread.tree_id)
        return self.expand_move_list(queryset, thread, user)