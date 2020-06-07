from datetime import timedelta

from django import dispatch
from django import http
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from django.utils import timezone

from tulius.forum import plugins
from tulius.forum.comments import forms
from tulius.forum.comments import pagination

ERROR_VALIDATION = _('there were some errors during form validation')


class CommentsCore(plugins.ForumPlugin):
    COMMENTS_ON_PAGE = 25

    def get_parent_comment(self, user, comment_id, check_write):
        try:
            comment_id = int(comment_id)
        except:
            raise http.Http404()
        models = self.site.core.models
        try:
            parent_comment = models.Comment.objects.select_related(
                'parent').get(id=comment_id, plugin_id=self.site_id)
        except models.Comment.DoesNotExist:
            raise http.Http404()
        parent_thread = parent_comment.parent
        if not parent_thread.read_right(user):
            raise http.Http404()
        if check_write and (not parent_thread.write_right(user)):
            raise http.Http404()
        return parent_thread, parent_comment

    # pylint: disable=too-many-branches,too-many-arguments
    def process_edit_comment(
            self, request, parent_thread, comment, reply, voting_enabled,
            voting_valid):
        adding = comment is None
        if comment and (comment.parent_id != parent_thread.id):
            raise http.Http404()
        initial = {}
        if comment:
            initial['title'] = comment.title
            initial['body'] = comment.body
            initial['voting'] = comment.voting
        else:
            initial['title'] = "Re: " + parent_thread.title

        form = forms.CommentForm(
            voting_enabled, initial=initial, data=request.POST or None)
        if comment:
            form.caption = _('edit post')
        else:
            form.caption = _('add post')

        if request.method == 'POST':
            if form.is_valid():
                if comment:
                    now = timezone.now()
                    comment.editor = request.user
                    if (
                            (comment.editor_id != comment.user_id) or
                            ((not comment.edit_time) and
                             (now > comment.create_time +
                              timedelta(minutes=2))) or
                            (comment.edit_time and (
                                now > comment.edit_time +
                                timedelta(minutes=2)))):
                        comment.edit_time = now
                else:
                    comment = self.site.models.Comment(parent=parent_thread)
                    comment.user = request.user
                comment.title = form.cleaned_data['title'] or ''
                comment.title = comment.title[:120]
                comment.body = form.cleaned_data['body']
                if voting_enabled:
                    comment.voting = form.cleaned_data['voting']
                comment.plugin_id = self.site_id
                voting_valid = (not voting_enabled) or (
                    voting_valid or (not comment.voting))
                if voting_valid:
                    comment.save()
                    if adding:
                        messages.success(
                            request, _('comment was successfully added'))
                    else:
                        messages.success(
                            request, _('comment was successfully updated'))
                else:
                    comment = None
                    messages.error(request, ERROR_VALIDATION)
            else:
                messages.error(request, ERROR_VALIDATION)
        return form, comment

    def get_comments_page(self, user, parent_thread, page_num):
        comments = self.site.core.models.Comment.objects.select_related('user')
        comments = comments.filter(
            parent=parent_thread, page=page_num).exclude(deleted=True)
        for comment in comments:
            comment.view_user = user
            comment.parent = parent_thread
        if comments and (page_num == 0):
            parent_thread.first_comment = comments[0]
        self.read_comments_signal.send(
            parent_thread, user=user, comments=comments)
        return comments

    def delete_comment(self, user, comment_id, message):
        models = self.site.models
        success = 'error'
        error_text = ''
        redirect = ''
        text = ''
        comment = None
        try:
            comment_id = int(comment_id)
            comment = models.Comment.objects.select_for_update(

            ).select_related('parent').get(id=comment_id)
        except:
            error_text = _(
                'Comment not found %(post_id)s.') % {'post_id': comment_id}
        if comment:
            if comment.is_thread():
                return self.site.core.delete_thread(
                    user, comment.parent_id, message)
            if not ((comment.user_id == user.id) or
                    comment.parent.moderate_right(user)):
                error_text = _(
                    'You have no rights to delete comment %(post_id)s.'
                ) % {'post_id': comment_id}
            else:
                comment.deleted = True
                delete_mark = models.CommentDeleteMark(
                    comment=comment, user=user, description=message)
                comment.save()
                delete_mark.save()
                redirect = comment.parent.get_absolute_url
            success = 'success'
            text = _('Comment successfully deleted!')
        return success, error_text, redirect, text

    def thread_pages_count(self, thread):
        return int(
            (thread.comments_count - 1) / self.COMMENTS_ON_PAGE + 1) or 1

    def get_comments_pagination(self, request, thread, page):
        pages = thread.pages_count
        pagination_context = pagination.get_pagination_context(
            request, page, pages)
        pagination_top = pagination.get_custom_pagination(
            request, pagination_context)
        pagination_context['bottom'] = True
        reply_form = forms.CommentForm(True) if thread.write_right() else None
        return {
            'pages': pages,
            'pagination_context': pagination_context,
            'reply_form': reply_form,
            'pagination': pagination_top,
            'pagination_bottom': pagination.get_custom_pagination(
                request, pagination_context)
        }

    def before_add_comment(self, **kwargs):
        thread = kwargs['sender']
        instance = kwargs['instance']
        comments_count = self.models.Comment.objects.filter(
            parent=thread, deleted=False).count()
        instance.page = int(comments_count / self.COMMENTS_ON_PAGE) + 1
        thread.comments_count += 1

    def before_delete_comment(self, sender, **kwargs):
        thread = kwargs['thread']
        if sender.id == thread.first_comment:
            thread.deleted = True
        else:
            thread.comments_count -= 1

    def get_thread_first_comment(self, thread):
        if thread.first_comment:
            try:
                return self.models.Comment.objects.get(id=thread.first_comment)
            except self.models.Comment.DoesNotExist:
                pass
        first_comment = self.models.Comment(
            parent=thread, title=thread.title, body=thread.body,
            user=thread.user)
        first_comment.save()
        thread.first_comment = first_comment.id
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
            sender.first_comment = comments.order_by('id')[0]
            sender.last_comment = comments.order_by('-id')[0]
            sender.comments_count = comments_count
            self.thread_update_comments_pages(sender)

    def thread_first_comment(self, thread):
        comment = getattr(thread, 'first_comment_cache', None)
        if comment:
            return comment
        if thread.first_comment_id:
            try:
                comment = self.Comment.objects.select_related('user').get(
                    id=thread.first_comment_id)
                comment.parent = thread
            except self.Comment.DoesNotExist:
                comment = None
        elif not thread.room:
            comment = self.Comment(user=thread.user, parent=thread)
            comment.title = thread.title
            comment.body = thread.body
            comment.save()
            thread.first_comment_id = comment.id
            thread.save()
        thread.first_comment_cache = comment
        return comment

    def thread_last_comment(self, thread):
        comment = getattr(thread, 'last_comment_cache', None)
        if comment:
            return comment
        if thread.last_comment_id:
            try:
                comment = self.Comment.objects.select_related('user').get(
                    id=thread.last_comment_id)
            except self.Comment.DoesNotExist:
                comment = None
        else:
            comment = thread.first_comment
            if comment:
                thread.last_comment_id = comment.id
                thread.save()
        thread.last_comment_cache = comment
        return comment

    def thread_view(self, sender, **kwargs):
        if sender:
            context = kwargs['context']
            user = kwargs['user']
            request = kwargs['request']
            page_num = request.GET['page'] if 'page' in request.GET else 1
            context['comments'] = self.get_comments_page(
                user, sender, int(page_num))

    def init_core(self):
        self.Comment = self.models.Comment
        self.read_comments_signal = dispatch.Signal(
            providing_args=["user", "comments"])
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
        self.view_comments_page = dispatch.Signal(
            providing_args=["json", "page", "comments", "thread"])
        self.comment_before_edit = dispatch.Signal(
            providing_args=["comment", "context"])
        self.comment_after_edit = dispatch.Signal(
            providing_args=["comment", "context", "adding"])
        self.comment_before_fastreply = dispatch.Signal(
            providing_args=["context"])
        self.comment_after_fastreply = dispatch.Signal()
        self.core['get_parent_comment'] = self.get_parent_comment
        self.core['process_edit_comment'] = self.process_edit_comment
        self.core['get_comments_page'] = self.get_comments_page
        self.core['delete_comment'] = self.delete_comment
        self.core['get_comments_pagination'] = self.get_comments_pagination
        self.core['Thread_get_first_comment'] = self.get_thread_first_comment
        self.core['Thread_pages_count'] = self.thread_pages_count
        self.core['Thread_first_comment'] = self.thread_first_comment
        self.core['Thread_last_comment'] = self.thread_last_comment
        self.signals['read_comments'] = self.read_comments_signal
        self.signals['before_add_comment'] = self.before_add_comment_signal
        self.signals['before_delete_comment'] = \
            self.before_delete_comment_signal
        self.signals['after_add_comment'] = self.after_add_comment_signal
        self.signals['after_delete_comment'] = self.after_delete_comment_signal
        self.signals['before_save_comment'] = self.before_save_comment_signal
        self.signals['comment_before_edit'] = self.comment_before_edit
        self.signals['comment_after_edit'] = self.comment_after_edit
        self.signals['comment_before_fastreply'] = \
            self.comment_before_fastreply
        self.signals['comment_after_fastreply'] = self.comment_after_fastreply
        self.signals['view_comments_page'] = self.view_comments_page
        self.before_add_comment_signal.connect(self.before_add_comment)
        self.before_delete_comment_signal.connect(self.before_delete_comment)
        self.after_add_comment_signal.connect(self.after_add_comment)
        self.after_delete_comment_signal.connect(self.after_delete_comment)

    def post_init(self):
        self.site.signals.thread_repair_counters.connect(
            self.repair_thread_counters)
        self.site.signals.thread_view.connect(self.thread_view)
