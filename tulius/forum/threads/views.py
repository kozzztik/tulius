from django.http import HttpResponseRedirect
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
