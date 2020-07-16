from django import http
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
