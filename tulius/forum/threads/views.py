from django import http
from django.http import Http404, HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.views import generic
from tulius.forum.plugins import BasePluginView


class BaseThreadView(BasePluginView):
    template_name = None
    parent_is_room = False
    view_mode = True

    def get_context_data(self, **kwargs):
        self.get_parent_thread(**kwargs)
        context = super(BaseThreadView, self).get_context_data(**kwargs)
        context['parent_thread'] = self.parent_thread
        if self.parent_thread and self.view_mode:
            self.site.signals.thread_view.send(
                self.parent_thread, context=context,
                user=self.request.user, request=self.request)
        return context

    def get_parent_thread(self, **kwargs):
        parent_id = kwargs['parent_id'] if 'parent_id' in kwargs else None
        self.user = self.request.user
        self.parent_thread = self.core.get_parent_thread(
            self.user, parent_id, self.parent_is_room) if parent_id else None


class Index(generic.TemplateView):
    template_name = 'base_vue.html'


class EditView(BaseThreadView):
    template_name = 'edit_thread'
    parent_is_room = True
    self_is_room = True
    require_user = True
    view_mode = False

    def get_context_data(self, **kwargs):
        context = super(EditView, self).get_context_data(**kwargs)
        parent_thread = self.parent_thread
        thread_id = self.kwargs['thread_id'] if \
            'thread_id' in self.kwargs else None
        thread = self.core.get_parent_thread(
            self.user, thread_id, self.self_is_room) if thread_id else None
        context['thread'] = thread
        if thread_id:
            parent_thread = thread.parent
            context['parent_thread'] = parent_thread
            if not thread.edit_right():
                raise Http404()
        else:
            if parent_thread is None:
                if (not self.user.is_superuser) or (not self.self_is_room):
                    raise Http404()
            else:
                if self.self_is_room:
                    if not parent_thread.moderate_right():
                        raise Http404()
                else:
                    if not parent_thread.write_right():
                        raise Http404()
        self.parent_thread = parent_thread
        self.adding = not bool(thread)
        self.edit_is_valid = True
        self.site.signals.thread_before_edit.send(
            self, thread=thread, context=context)
        (form, formset, thread, comment) = self.core.process_edit_thread(
            self.request, parent_thread, thread, True, self.edit_is_valid)
        context['comment'] = comment
        context['form'] = form
        context['formset'] = formset
        context['thread'] = thread
        if not self.parent_thread:
            context['parent_thread'] = thread
        self.thread = thread
        self.comment = comment
        if not thread_id:
            context['form_submit_title'] = _("add")
        context['show_preview'] = not self.self_is_room
        self.site.signals.thread_after_edit.send(
            self, thread=thread, context=context)
        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if self.thread:
            return http.HttpResponseRedirect(self.thread.get_absolute_url)
        return self.render_to_response(context)


class MoveThreadSelect(BaseThreadView):
    template_name = 'thread_move_select'
    parent_is_room = None

    def get_context_data(self, **kwargs):
        context = super(MoveThreadSelect, self).get_context_data(**kwargs)
        threads = self.core.thread_move_list(self.parent_thread, self.user)
        for thread in threads:
            if thread:
                thread.move_url = self.core.move_thread_confirm_url(
                    self.parent_thread, thread)
        context['threads'] = threads
        if self.request.user.is_superuser:
            context['index_url'] = self.core.move_thread_confirm_url(
                self.parent_thread, None)
        return context


class MoveThreadConfirm(BaseThreadView):
    template_name = 'thread_move_confirm'
    parent_is_room = None

    def get_context_data(self, **kwargs):
        context = super(MoveThreadConfirm, self).get_context_data(**kwargs)
        thread_id = self.kwargs['thread_id'] if \
            'thread_id' in self.kwargs else None
        thread = self.core.get_parent_thread(
            self.user, thread_id, True) if thread_id else None
        self.thread = thread
        context['thread'] = thread
        return context

    def post(self, request, **kwargs):
        self.get_context_data(**kwargs)
        self.core.move_thread(self.parent_thread, request.user, self.thread)
        return HttpResponseRedirect(self.parent_thread.get_absolute_url)
