from django.conf.urls import url

# TODO: fix this when module moved
from tulius.forum.plugins import ForumPlugin
from tulius.stories.models import Role
from tulius.games.models import Game
from .views import GameIndex, VariationIndex, Fix


class GamePlugin(ForumPlugin):

    def game_url(self, game):
        return self.reverse('game', game.id)

    def variation_url(self, variation):
        return self.reverse('variation', variation.id)

    def copy_game_post(self, thread, new_parent, variation, rolelinks):
        models = self.site.models
        gamemodels = self.site.gamemodels
        subthreads = models.Thread.objects.filter(parent=thread, deleted=False)
        rights = gamemodels.GameThreadRight.objects.filter(thread=thread)
        old_thread = thread
        thread = models.Thread(
            title=old_thread.title, parent=new_parent,
            body=old_thread.body, room=old_thread.room, user=old_thread.user,
            access_type=old_thread.access_type,
            create_time=old_thread.create_time, closed=old_thread.closed,
            important=old_thread.important, plugin_id=self.site_id,
            media=old_thread.media,
        )
        role_id = old_thread.data1
        if role_id and (role_id in rolelinks):
            thread.data1 = rolelinks[role_id].id
        thread.save()
        if not new_parent:
            variation.thread = thread
            variation.save()
        thread.variation = variation
        for right in rights:
            right.id = None
            right.thread = thread
            if right.role_id and (right.role_id in rolelinks):
                right.role = rolelinks[right.role_id]
            right.save()
        for subpost in subthreads:
            self.copy_game_post(subpost, thread, variation, rolelinks)

        if not old_thread.room:
            first_comment = None
            subcomments = models.Comment.objects.filter(
                parent=old_thread, deleted=False)
            for comment in subcomments:
                new_comment = models.Comment(
                    parent=thread, title=comment.title, body=comment.body,
                    plugin_id=self.site_id,
                    user=comment.user, create_time=comment.create_time,
                    media=comment.media)
                new_comment.reply_id = first_comment
                if comment.data1 and (comment.data1 in rolelinks):
                    new_comment.data1 = rolelinks[comment.data1].id
                new_comment.save()
                if not first_comment:
                    first_comment = new_comment.id
        return thread

    def create_gameforum(self, user, variation):
        models = self.site.models
        if variation.game:
            title = variation.game.name
        else:
            title = variation.name
        thread = models.Thread(
            title=title, user=user,
            access_type=models.THREAD_ACCESS_TYPE_OPEN,
            room=True, plugin_id=self.site_id)
        thread.save()
        return thread

    def copy_game_forum(self, variation, rolelinks, user):
        if not variation.thread:
            variation.thread = self.create_gameforum(user, variation)
            variation.save()
        thread = self.copy_game_post(
            variation.thread, None, variation, rolelinks)
        thread.title = variation.game.name
        thread.save()
        return thread

    def fix_games(self):
        games = Game.objects.all()
        for game in games:
            variation = game.variation
            root_thread = variation.thread
            if not root_thread:
                continue
            tree_id = root_thread.tree_id
            roles = Role.objects.filter(variation=variation)
            for role in roles:
                comments = self.models.Comment.objects.filter(
                    parent__tree_id=tree_id, deleted=False, data1=role.id)
                role.comments_count = comments.count()
                role.save()
            variation.comments_count = self.models.Comment.objects.filter(
                parent__tree_id=tree_id, deleted=False).count()
            variation.save()

    def init_core(self):
        super(GamePlugin, self).init_core()
        self.urlizer['game'] = self.game_url
        self.urlizer['variation'] = self.variation_url
        self.core['copy_game_forum'] = self.copy_game_forum
        self.core['create_gameforum'] = self.create_gameforum
        self.core['fix_games'] = self.fix_games
        self.templates['fix_games'] = 'gameforum/fix.haml'

    def get_urls(self):
        return [
            url(
                r'^game/(?P<game_id>\d+)/$',
                GameIndex.as_view(plugin=self),
                name='game'),
            url(
                r'^variation/(?P<variation_id>\d+)/$',
                VariationIndex.as_view(plugin=self),
                name='variation'),
            url(
                r'^fix/$',
                Fix.as_view(plugin=self),
                name='fix'),
        ]
