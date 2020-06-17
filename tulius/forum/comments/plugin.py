from django.conf.urls import url

from .core import CommentsCore
from .views import EditComment, CommentRedirrect, Preview


class CommentsPlugin(CommentsCore):
    comment_template = 'forum/snippets/post.haml'
    edit_comment_template = 'forum/add_post.haml'

    def get_paged_url(self, comment):
        return "%s?page=%s#%s" % (
            self.reverse('thread', comment.parent_id),
            comment.page, comment.id)

    def comment_url(self, comment):
        # TODO hope this wouldn't crush nothing. refactor all of that.
        return self.get_paged_url(comment)

    def get_page_num(self, comment):
        num = self.models.Comment.objects.filter(
            parent=comment.parent, id__lt=comment.id, deleted=False).count()
        return (num / self.COMMENTS_ON_PAGE) + 1

    def reply_url(self, comment):
        return self.reverse('add_comment', comment.id)

    def get_edit_url(self, comment):
        if comment.is_thread():
            return comment.parent.get_edit_url
        return self.reverse('edit_comment', comment.id)

    def init_core(self):
        super(CommentsPlugin, self).init_core()
        self.templates['add_comment'] = self.edit_comment_template
        self.templates['comment'] = self.comment_template
        self.templates['comment_player'] = 'forum/comments/avatar.haml'
        self.templates['comment_preview'] = 'forum/preview.haml'
        self.urlizer['comment'] = self.comment_url
        self.urlizer['comment_paged'] = self.get_paged_url
        self.urlizer['Comment_get_paged_url'] = self.get_paged_url
        self.urlizer['Comment_get_absolute_url'] = self.comment_url
        self.urlizer['Comment_get_reply_url'] = self.reply_url
        self.urlizer['Comment_get_edit_url'] = self.get_edit_url
        self.core['Comment_get_page_num'] = self.get_page_num

    def get_urls(self):
        return [
            url(
                r'^add_comment/(?P<reply_id>\d+)/$',
                EditComment.as_view(plugin=self),
                name='add_comment'),
            url(
                r'^edit_comment/(?P<comment_id>\d+)/$',
                EditComment.as_view(plugin=self),
                name='edit_comment'),
            url(
                r'^comment/(?P<comment_id>\d+)/$',
                CommentRedirrect.as_view(plugin=self),
                name='comment'),
            url(r'^preview/$', Preview.as_view(plugin=self), name='preview'),
        ]
