# TODO: fix this when module moved
from tulius.forum.plugins import ForumPlugin
from tulius.gameforum import core


class GamePlugin(ForumPlugin):
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

    def copy_game_forum(self, variation, rolelinks, user):
        if not variation.thread:
            variation.thread = core.create_game_forum(user, variation)
            variation.save()
        thread = self.copy_game_post(
            variation.thread, None, variation, rolelinks)
        thread.title = variation.game.name
        thread.save()
        return thread

    def init_core(self):
        super(GamePlugin, self).init_core()
        self.core['copy_game_forum'] = self.copy_game_forum
