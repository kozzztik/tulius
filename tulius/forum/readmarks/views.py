from django import http

from tulius.forum import plugins


class MarkAsRead(plugins.BasePluginView):
    require_user = True

    def mark_as_readed(self, parent_thread, user):
        threads = parent_thread.get_children()
        if not parent_thread:
            threads = threads.filter(plugin=None)
        for thread in threads:
            thread.parent = parent_thread
        threads = [thread for thread in threads if thread.read_right(user)]
        for thread in threads:
            if thread.room:
                self.mark_as_readed(thread, user)
            else:
                thread.mark_as_readed()  # TODO may not work

    def get(self, request, thread_id=None, **kwargs):
        if thread_id:
            try:
                thread_id = int(thread_id)
            except:
                raise http.Http404()
            parent_thread = self.core.get_parent_thread(
                request.user, thread_id)
            self.mark_as_readed(parent_thread, request.user)
            return http.HttpResponseRedirect(parent_thread.get_absolute_url)
        threads = self.core.models.Thread.objects.filter(
            parent=None, plugin_id=self.site.site_id)
        for thread in threads:
            self.mark_as_readed(thread, request.user)
        return http.HttpResponseRedirect(self.site.urlizer.index())
