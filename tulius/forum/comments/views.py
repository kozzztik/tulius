from django.utils.translation import ugettext_lazy as _
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.utils.timezone import now
from django import http
import json
from .plugin import BasePluginView
from .forms import CommentForm, CommentDeleteForm
from .pagination import get_custom_pagination, get_pagination_context


class BaseCommentView(BasePluginView):
    def get_context_data(self, **kwargs):
        context = super(BaseCommentView, self).get_context_data(**kwargs)
        reply_id = kwargs['reply_id'] if 'reply_id' in kwargs else None
        self.comment_id = kwargs[
            'comment_id'] if 'comment_id' in kwargs else None
        self.comment = None
        self.reply = None
        if not (reply_id or self.comment_id):
            raise Http404()
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
                raise Http404()
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
        return self.render_to_response(context, current_app=self.site.app_name)


ERROR_VALIDATION = _('there were some errors during form validation')


class FastReply(BaseCommentView):
    template_name = 'fast_reply'
    require_user = True
    error_message = None

    def get_context_data(self, **kwargs):
        context = super(FastReply, self).get_context_data(**kwargs)
        context['parent_comment'] = self.comment
        if not self.parent_thread.write_right():
            raise Http404()
        context['error_message'] = self.error_message
        context['reply_form'] = CommentForm(True)
        self.form = CommentForm(True, data=self.request.POST or None)
        context['form'] = self.form
        self.site.signals.comment_before_fastreply.send(self, context=context)
        return context

    def post(self, request, *args, **kwargs):
        html = self.render(**kwargs)
        comment = None
        error_message = ''
        self.comment = None
        if self.form.is_valid():
            comment = self.core.models.Comment(plugin_id=self.plugin.site_id)
            comment.parent_id = self.parent_thread.id
            comment.user = request.user
            comment.title = "Re: " + self.parent_thread.title
            comment.body = self.form.cleaned_data['body']
            comment.reply = self.comment
            comment.save()
            self.comment = comment
        else:
            error_message = ERROR_VALIDATION
        ret_json = {'error_message': str(error_message), 'form': html}
        self.site.signals.comment_after_fastreply.send(self)
        if comment:
            ret_json['id'] = comment.id
            ret_json['page'] = comment.page
        return HttpResponse(json.dumps(ret_json))


class CommentsPage(BasePluginView):
    template_name = 'comments'

    def get_context_data(self, **kwargs):
        context = super(CommentsPage, self).get_context_data(**kwargs)
        self.parent_thread = self.core.get_parent_thread(
            self.request.user, kwargs['thread_id'], False)
        context['parent_thread'] = self.parent_thread
        self.page_num = self.request.GET[
            'page_num'] if 'page_num' in self.request.GET else 1
        self.pages = self.parent_thread.pages_count
        try:
            self.page_num = int(self.page_num)
        except:
            raise Http404()
        self.comments = self.core.get_comments_page(
            self.request.user, self.parent_thread, self.page_num)
        context['comments'] = self.comments
        return context

    def get(self, request, *args, **kwargs):
        html = self.render(**kwargs)
        pagination_context = get_pagination_context(
            request, self.page_num, self.pages)
        pagination_context['bottom'] = False
        pagination_top = get_custom_pagination(request, pagination_context)
        pagination_context['bottom'] = True
        pagination_bottom = get_custom_pagination(request, pagination_context)
        ret_json = dict(html=html, pagination=pagination_top)
        ret_json['pagination_bottom'] = pagination_bottom
        self.site.signals.view_comments_page.send(
            self, json=ret_json, comments=self.comments, page=self.page_num,
            thread=self.parent_thread)
        return HttpResponse(json.dumps(ret_json))


class CommentRedirrect(BaseCommentView):
    def get(self, request, *args, **kwargs):
        self.get_context_data(**kwargs)
        if self.parent_thread.check_deleted():
            raise Http404(str(_('Post was deleted')))
        if self.comment.deleted:
            raise Http404(str(_('Comment was deleted')))
        return HttpResponseRedirect(
            self.site.urlizer.comment_paged(self.comment))


class Preview(BasePluginView):
    template_name = 'comment_preview'
    require_user = True

    def get_context_data(self, **kwargs):
        context = super(Preview, self).get_context_data(**kwargs)
        context['body'] = self.request.POST[
            'body'] if 'body' in self.request.POST else ''
        context['title'] = self.request.POST[
            'title'] if 'title' in self.request.POST else ''
        context['create_time'] = now()
        return context

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)


class DeleteComment(BasePluginView):
    def post(self, request, *args, **kwargs):
        form = CommentDeleteForm(data=request.POST or None)
        success = 'error'
        text = ''
        redirect = ''
        if not form.is_valid():
            error_text = _('Form not valid')
        else:
            comment_id = form.cleaned_data['post']
            message = form.cleaned_data['message']
            (success, error_text, redirect, text) = self.core.delete_comment(
                request.user, comment_id, message)
        return HttpResponse(
            json.dumps(
                {
                    'result': success,
                    'error_text': str(error_text),
                    'redirect': redirect,
                    'text': str(text)
                }))
