from django.utils.translation import ugettext_lazy as _, pgettext
# TODO: fix this when module moved
from tulius.forum.comments.plugin import CommentsPlugin
from tulius.stories.models import *


class GameCommentsPlugin(CommentsPlugin):
    comment_template = 'gameforum/snippets/post.haml'
    fast_reply_template = 'gameforum/snippets/fast_reply.haml'
    edit_comment_template = 'gameforum/add_post.haml'
    
    def reply_str(self, comment):
        sex = comment.role.sex if comment.role else None
        name = comment.role.name if comment.role else _('Leader')
        if sex == CHAR_SEX_MALE:
            s = pgettext('He', '%s said')
        elif sex == CHAR_SEX_FEMALE:
            s = pgettext('She', '%s said')
        elif sex == CHAR_SEX_MIDDLE:
            s = pgettext('It', '%s said')
        elif sex == CHAR_SEX_PLUR:
            s = pgettext('They', '%s said')
        else:
            s = pgettext('Someone', '%s said')
        return s % name
    
    def update_role_comments_count(self, role_id, count):
        if role_id:
            role = Role.objects.get(id=role_id)
            role.comments_count += count
            role.save() 
            
    def after_add_comment(self, sender, **kwargs):
        thread = kwargs['thread']
        variation = Variation.objects.get(thread__tree_id=thread.tree_id)
        variation.comments_count += 1
        variation.save()
        self.update_role_comments_count(sender.data1, 1) 
        
    def before_delete_comment(self, sender, **kwargs):
        super(GameCommentsPlugin, self).before_delete_comment(sender, **kwargs)
        thread = kwargs['thread']
        variation = Variation.objects.get(thread__tree_id=thread.tree_id)
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
