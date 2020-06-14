from django import dispatch
from django import urls
from django.utils.translation import ugettext_lazy as _, pgettext
from django.utils import html
from djfw.wysibb.templatetags import bbcodes

from tulius.forum import signals
from tulius.gameforum import consts
from tulius.gameforum import threads
from tulius.forum.comments import api as comments
from tulius.forum.comments import plugin
from tulius.stories import models


class GameCommentsPlugin(plugin.CommentsPlugin):
    comment_template = 'gameforum/snippets/post.haml'
    fast_reply_template = 'gameforum/snippets/fast_reply.haml'
    edit_comment_template = 'gameforum/add_post.haml'

    def reply_str(self, comment):
        sex = comment.role.sex if comment.role else None
        name = comment.role.name if comment.role else _('Leader')
        if sex == models.CHAR_SEX_MALE:
            s = pgettext('He', '%s said')
        elif sex == models.CHAR_SEX_FEMALE:
            s = pgettext('She', '%s said')
        elif sex == models.CHAR_SEX_MIDDLE:
            s = pgettext('It', '%s said')
        elif sex == models.CHAR_SEX_PLUR:
            s = pgettext('They', '%s said')
        else:
            s = pgettext('Someone', '%s said')
        return s % name

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


@dispatch.receiver(signals.thread_room_to_json)
def room_to_json(sender, thread, response, **kwargs):
    if thread.plugin_id != consts.GAME_FORUM_SITE_ID:
        return
    if thread.last_comment is None:
        return
    response['last_comment'] = {
        'id': thread.last_comment.id,
        'parent_id': thread.last_comment.parent_id,
        'page': thread.last_comment.page,
        'user': sender.role_to_json(thread.last_comment.data1),
        'create_time': thread.last_comment.create_time,
    }


class CommentsBase(threads.BaseThreadAPI, comments.CommentsBase):
    def comment_url(self, comment):
        return urls.reverse(
            'game_forum_api:comment', kwargs={
                'pk': comment.id,
                'variation_id': self.variation.id,
            })

    def comment_to_json(self, c):
        return {
            'id': c.id,
            'url': self.comment_url(c),
            'title': html.escape(c.title),
            'body': bbcodes.bbcode(c.body),
            'user': self.role_to_json(c.data1, detailed=True),
            'create_time': c.create_time,
            'voting': c.voting,
            'edit_right': self.comment_edit_right(c),
            'is_thread': c.is_thread(),
            'edit_time': c.edit_time,
            'editor': self.role_to_json(c.data2) if c.editor else None
        }


class CommentsPageAPI(comments.CommentsPageAPI, CommentsBase):
    pass


class CommentAPI(comments.CommentAPI, CommentsBase):
    pass
