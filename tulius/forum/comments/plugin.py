from django.conf.urls import url

from .core import CommentsCore
from .views import EditComment, FastReply, CommentsPage, \
    CommentRedirrect, Preview, DeleteComment


class CommentsPlugin(CommentsCore):
    comment_template = 'forum/snippets/post.haml'
    fast_reply_template = 'forum/snippets/fast_reply_form.haml'
    edit_comment_template = 'forum/add_post.haml'

    def get_paged_url(self, comment):
        return "%s?page=%s#%s" % (
            comment.parent.get_absolute_url, comment.page, comment.id)

    def comment_url(self, comment):
        return self.reverse('comment', comment.id)

    def delete_comment_url(self):
        return self.reverse('delete_comment')

    def thread_comments_page_url(self, thread):
        return self.reverse('comments_page', thread.id)

    def get_page_num(self, comment):
        num = self.models.Comment.objects.filter(
            parent=comment.parent, id__lt=comment.id, deleted=False).count()
        return (num / self.COMMENTS_ON_PAGE) + 1

    def reply_url(self, comment):
        return self.reverse('add_comment', comment.id)

    def fast_reply_url(self, comment):
        return self.reverse('fast_reply', comment.id)

    def get_edit_url(self, comment):
        if comment.is_thread():
            return comment.parent.get_edit_url
        return self.reverse('edit_comment', comment.id)

    def reply_str(self, comment):
        return comment.user.get_forum_reply_str()

    def init_core(self):
        super(CommentsPlugin, self).init_core()
        self.templates['add_comment'] = self.edit_comment_template
        self.templates['fast_reply'] = self.fast_reply_template
        self.templates['comments'] = 'forum/comments.haml'
        self.templates['comment'] = self.comment_template
        self.templates['comment_player'] = 'forum/comments/avatar.haml'
        self.templates['comment_preview'] = 'forum/preview.haml'
        self.templates['thread_latest_post'] = \
            'forum/snippets/latest_post.haml'
        self.urlizer['comment'] = self.comment_url
        self.urlizer['comment_paged'] = self.get_paged_url
        self.urlizer['Comment_get_paged_url'] = self.get_paged_url
        self.urlizer['Comment_get_absolute_url'] = self.comment_url
        self.urlizer['Comment_get_delete_url'] = self.delete_comment_url
        self.urlizer['Comment_get_reply_url'] = self.reply_url
        self.urlizer['Comment_get_fast_reply_url'] = self.fast_reply_url
        self.urlizer['Comment_get_edit_url'] = self.get_edit_url
        self.urlizer['Comment_reply_str'] = self.reply_str

        self.urlizer['delete_comment'] = self.delete_comment_url
        self.urlizer['Thread_comments_page_url'] = \
            self.thread_comments_page_url
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
                r'^fast_reply/(?P<comment_id>\d+)/$',
                FastReply.as_view(plugin=self),
                name='fast_reply'),
            url(
                r'^comment/(?P<comment_id>\d+)/$',
                CommentRedirrect.as_view(plugin=self),
                name='comment'),
            url(
                r'^comments_page/(?P<thread_id>\d+)/$',
                CommentsPage.as_view(plugin=self),
                name='comments_page'),
            url(
                r'^delete_comment/$',
                DeleteComment.as_view(plugin=self),
                name='delete_comment'),
            url(r'^preview/$', Preview.as_view(plugin=self), name='preview'),
        ]
