from django import dispatch
from django.utils.translation import ugettext_lazy as _

from tulius.forum import plugins


ERROR_VALIDATION = _('there were some errors during form validation')


class CommentsCore(plugins.ForumPlugin):
    COMMENTS_ON_PAGE = 25

    def thread_pages_count(self, thread):
        return int(
            (thread.comments_count - 1) / self.COMMENTS_ON_PAGE + 1) or 1

    def before_add_comment(self, **kwargs):
        thread = kwargs['sender']
        instance = kwargs['instance']
        comments_count = self.models.Comment.objects.filter(
            parent=thread, deleted=False).count()
        instance.page = int(comments_count / self.COMMENTS_ON_PAGE) + 1
        thread.comments_count += 1

    def before_delete_comment(self, sender, **kwargs):
        thread = kwargs['thread']
        if sender.id == thread.first_comment_id:
            thread.deleted = True
        else:
            thread.comments_count -= 1

    def get_thread_first_comment(self, thread):
        if thread.first_comment_id:
            try:
                return self.models.Comment.objects.get(
                    id=thread.first_comment_id)
            except self.models.Comment.DoesNotExist:
                pass
        first_comment = self.models.Comment(
            parent=thread, title=thread.title, body=thread.body,
            user=thread.user)
        first_comment.save()
        thread.first_comment_id = first_comment.id
        thread.save()
        return first_comment

    def thread_update_comments_pages(self, thread):
        model = self.models.Comment
        comments_query = model.objects.filter(parent=thread, deleted=False)
        pages_count = self.thread_pages_count(thread)
        for x in range(pages_count):
            comments = comments_query[
                self.COMMENTS_ON_PAGE * x: self.COMMENTS_ON_PAGE * (x + 1)]
            comments = comments.values('id')
            comments = [comment['id'] for comment in comments]
            model.objects.filter(id__in=comments).update(page=(x + 1))

    def after_add_comment(self, sender, **kwargs):
        if kwargs['restore']:
            self.thread_update_comments_pages(kwargs['thread'])

    def after_delete_comment(self, sender, **kwargs):
        self.thread_update_comments_pages(kwargs['thread'])

    def repair_thread_counters(self, sender, **args):
        if sender.room:
            return
        comments = self.models.Comment.objects.filter(
            parent=sender, deleted=False)
        comments_count = comments.count()
        if comments_count:
            sender.first_comment_id = comments.order_by('id')[0].pk
            sender.last_comment_id = comments.order_by('-id')[0].pk
            sender.comments_count = comments_count
            self.thread_update_comments_pages(sender)

    def init_core(self):
        self.Comment = self.models.Comment
        self.before_add_comment_signal = dispatch.Signal(
            providing_args=["instance", "restore"])
        self.before_delete_comment_signal = dispatch.Signal(
            providing_args=["thread"])
        self.after_add_comment_signal = dispatch.Signal(
            providing_args=["thread", "restore"])
        self.after_delete_comment_signal = dispatch.Signal(
            providing_args=["thread"])
        self.before_save_comment_signal = dispatch.Signal(
            providing_args=["old_comment"])
        self.core['Thread_get_first_comment'] = self.get_thread_first_comment
        self.core['Thread_pages_count'] = self.thread_pages_count
        self.signals['before_add_comment'] = self.before_add_comment_signal
        self.signals['before_delete_comment'] = \
            self.before_delete_comment_signal
        self.signals['after_add_comment'] = self.after_add_comment_signal
        self.signals['after_delete_comment'] = self.after_delete_comment_signal
        self.signals['before_save_comment'] = self.before_save_comment_signal
        self.before_add_comment_signal.connect(self.before_add_comment)
        self.before_delete_comment_signal.connect(self.before_delete_comment)
        self.after_add_comment_signal.connect(self.after_add_comment)
        self.after_delete_comment_signal.connect(self.after_delete_comment)

    def post_init(self):
        self.site.signals.thread_repair_counters.connect(
            self.repair_thread_counters)
