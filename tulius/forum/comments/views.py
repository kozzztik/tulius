from django import http
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from tulius.forum import plugins


class BaseCommentView(plugins.BasePluginView):
    def get_context_data(self, **kwargs):
        context = super(BaseCommentView, self).get_context_data(**kwargs)
        reply_id = kwargs['reply_id'] if 'reply_id' in kwargs else None
        self.comment_id = kwargs[
            'comment_id'] if 'comment_id' in kwargs else None
        self.comment = None
        self.reply = None
        if not (reply_id or self.comment_id):
            raise http.Http404()
        if reply_id:
            (self.parent_thread, self.reply) = self.core.get_parent_comment(
                self.request.user, reply_id, True)
        else:
            (self.parent_thread, self.comment) = self.core.get_parent_comment(
                self.request.user, self.comment_id, False)
        context['parent_thread'] = self.parent_thread
        return context


class EditComment(BaseCommentView):
    template_name = 'add_comment'
    require_user = True

    def get_context_data(self, **kwargs):
        context = super(EditComment, self).get_context_data(**kwargs)
        if self.comment:
            self.comment.view_user = self.request.user
            if not self.comment.edit_right:
                raise http.Http404()
        context['show_voting'] = True
        context['show_preview'] = True
        self.edit_is_valid = True
        self.site.signals.comment_before_edit.send(
            self, comment=self.comment, context=context)
        (form, comment) = self.core.process_edit_comment(
            self.request,
            self.parent_thread,
            self.comment,
            self.reply,
            True,
            self.edit_is_valid)
        context['form'] = form
        context['comment'] = comment
        self.comment = comment
        if not self.comment_id:
            context['form_submit_title'] = _("add")
        self.site.signals.comment_after_edit.send(
            self,
            comment=self.comment,
            context=context,
            adding=(self.comment_id is None))
        return context

    def post(self, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if self.comment:
            return http.HttpResponseRedirect(self.comment.get_absolute_url)
        return self.render_to_response(context)


ERROR_VALIDATION = _('there were some errors during form validation')


class CommentRedirrect(BaseCommentView):
    def get(self, request, *args, **kwargs):
        self.get_context_data(**kwargs)
        if self.parent_thread.check_deleted():
            raise http.Http404(str(_('Post was deleted')))
        if self.comment.deleted:
            raise http.Http404(str(_('Comment was deleted')))
        return http.HttpResponseRedirect(
            self.site.urlizer.comment_paged(self.comment))


class Preview(plugins.BasePluginView):
    template_name = 'comment_preview'
    require_user = True

    def get_context_data(self, **kwargs):
        context = super(Preview, self).get_context_data(**kwargs)
        context['body'] = self.request.POST[
            'body'] if 'body' in self.request.POST else ''
        context['title'] = self.request.POST[
            'title'] if 'title' in self.request.POST else ''
        context['create_time'] = timezone.now()
        return context

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)
