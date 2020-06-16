from tulius.forum.comments import plugin
from tulius.stories import models


class GameCommentsPlugin(plugin.CommentsPlugin):
    comment_template = 'gameforum/snippets/post.haml'
    edit_comment_template = 'gameforum/add_post.haml'

    def update_role_comments_count(self, role_id, count):
        if role_id:
            role = models.Role.objects.get(id=role_id)
            role.comments_count += count
            role.save()

    def after_add_comment(self, sender, **kwargs):
        thread = kwargs['thread']
        variation = models.Variation.objects.get(
            thread__tree_id=thread.tree_id)
        variation.comments_count += 1
        variation.save()
        self.update_role_comments_count(sender.data1, 1)

    def before_delete_comment(self, sender, **kwargs):
        super(GameCommentsPlugin, self).before_delete_comment(sender, **kwargs)
        thread = kwargs['thread']
        variation = models.Variation.objects.get(
            thread__tree_id=thread.tree_id)
        variation.comments_count -= 1
        variation.save()
        self.update_role_comments_count(sender.data1, -1)

    def before_save_comment(self, sender, **kwargs):
        old_comment = kwargs['old_comment']
        if sender.data1 != old_comment.data1:
            self.update_role_comments_count(old_comment.data1, -1)
            self.update_role_comments_count(sender.data1, 1)

    def init_core(self):
        super(GameCommentsPlugin, self).init_core()
        self.before_save_comment_signal.connect(self.before_save_comment)
        self.after_add_comment_signal.connect(self.after_add_comment)
