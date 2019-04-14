from django import dispatch
from django import http
from django import shortcuts
from django.core import exceptions
from django.utils.translation import ugettext_lazy as _

from djfw import inlineformsets

from tulius.forum import plugins
from tulius.forum.threads import forms


ERROR_VALIDATION = _('there were some errors during form validation')


class ThreadsCorePlugin(plugins.ForumPlugin):
    def get_parent_thread(self, user, thread_id, is_room=None):
        try:
            thread_id = int(thread_id)
        except:
            raise http.Http404()
        if is_room is None:
            parent_post = shortcuts.get_object_or_404(
                self.site.core.models.Thread,
                id=thread_id, plugin_id=self.site_id)
        else:
            parent_post = shortcuts.get_object_or_404(
                self.site.core.models.Thread,
                id=thread_id, plugin_id=self.site_id, room=is_room)
        if parent_post.check_deleted():
            raise http.Http404(str(_('Post was deleted')))
        if not parent_post.read_right(user):
            raise exceptions.PermissionDenied()
        return parent_post

    def room_descendants(self, user, room):
        if room.rght - room.lft <= 1:
            return [], []
        room_list = room.get_free_descendants.filter(room=True, deleted=False)
        room_list = [thread for thread in room_list]
        protected_threads = []
        if room.protected_threads:
            protected_threads = room.get_readeable_protected_descendants
            room_list += [
                thread for thread in protected_threads if thread.room]
        new_room_list = []
        while room_list:
            tested_room = room_list.pop(0)
            parent_id = tested_room.parent_id
            found_parent = (parent_id == room.id)
            if not found_parent:
                for tmp in room_list:
                    if tmp.id == parent_id:
                        found_parent = True
                        break
            if not found_parent:
                for tmp in new_room_list:
                    if tmp.id == parent_id:
                        found_parent = True
                        break
            if not found_parent:
                lft = tested_room.lft
                rght = tested_room.rght
                room_list = [
                    tmp for tmp in room_list if
                    not ((tmp.lft > lft) and (tmp.rght < rght))]
                new_room_list = [
                    tmp for tmp in new_room_list if
                    not ((tmp.lft > lft) and (tmp.rght < rght))]
            else:
                new_room_list += [tested_room]
        room_ids = [tmp.id for tmp in new_room_list]
        threads = room.get_free_descendants.filter(room=False, deleted=False)
        threads = [thread for thread in threads]
        if room.protected_threads:
            threads += [
                thread for thread in protected_threads if not thread.room]
        threads = [
            thread for thread in threads if
            (thread.parent_id == room.id) or (thread.parent_id in room_ids)]
        return new_room_list, threads

    def prepare_room_list(self, user, parent_room, rooms):
        site = self.site
        for thread in rooms:
            thread.parent = parent_room
            thread._site = site
        rooms = [thread for thread in rooms if thread.view_right(user)]
        for room in rooms:
            threads = self.room_descendants(user, room)[1]
            for thread in threads:
                thread.parent = room
                thread._site = site
            threads = [thread for thread in threads if thread.view_right(user)]
            room.threads_count = len(threads)
            self.thread_prepare_room_signal.send(
                room, parent_thread=parent_room, threads=threads, user=user)
        return rooms

    def paginate_thread(self, thread, base_url):
        class ThreadPage:
            page = 0
            page_link = ""

        childcount = self.site.models.Comment.objects.filter(
            parent=thread, deleted=False).count()
        pages = int((childcount - 1) / self.site.models.COMMENTS_ON_PAGE) + 1
        if pages > 1:
            thread.pages = []
            for i in range(pages):
                page = ThreadPage()
                page.page = i + 1
                page.url = "%s?page=%s" % (base_url, i + 1,)
                thread.pages += [page]

    def get_subthreads(self, user, parent_thread, is_room=False):
        models = self.site.models
        threads = models.Thread.objects.filter(
            parent=parent_thread, room=is_room).exclude(deleted=True)
        if not parent_thread:
            threads = threads.filter(plugin_id=self.site_id)
        if is_room:
            return self.prepare_room_list(user, parent_thread, threads)
        threads = threads.order_by('-last_comment_id')

        for thread in threads:
            thread.parent = parent_thread
        threads = [thread for thread in threads if thread.view_right(user)]

        for thread in threads:
            if thread.read_right(user):
                self.paginate_thread(thread, thread.get_absolute_url)
            if thread.access_type == models.THREAD_ACCESS_TYPE_NO_READ:
                thread.accessed_users = thread.get_accessed_users
        self.threads_list_signal.send(
            parent_thread, threads=threads, is_room=is_room)
        return threads

    def get_index(self, user, level):
        core = self.site.core
        childs = [child for child in core.get_free_index(user, level)]
        childs = childs + [
            child for child in core.get_readeable_protected_index(user, level)]
        childs = [thread for thread in childs if thread.room]
        return sorted(childs, key=lambda x: x.id)

    def process_edit_room(
            self, request, parent_thread, thread, formset_params=None):
        formset_params = formset_params or {}
        models = self.site.models
        right_model = self.site.core.right_model
        right_form = self.site.core.right_form
        adding = thread is None
        form = forms.RoomForm(models, thread, data=request.POST or None)
        form.room = True
        formset_params['parent_thread'] = parent_thread or thread
        formset = inlineformsets.get_formset(
            models.Thread, right_model, request.POST,
            base_form=right_form, extra=1, params=formset_params,
            instance=thread)
        if request.method == 'POST':
            if form.is_valid():
                if not thread:
                    thread = models.Thread(room=True)
                thread.title = form.cleaned_data['title']
                thread.body = form.cleaned_data['body']
                thread.access_type = form.cleaned_data['access_type']
                if not thread.id:
                    thread.user = request.user
                    thread.parent = parent_thread
                thread.plugin_id = self.site_id
                if formset.is_valid():
                    thread.save()
                    for form in formset:
                        if form.is_valid():
                            right = form.save(commit=False)
                            right.thread = thread
                            right.save()
                    if not adding:
                        formset.save()
                else:
                    thread = None
        return form, formset, thread

    # pylint: disable=too-many-branches,too-many-nested-blocks
    # pylint: disable=too-many-arguments,too-many-statements
    def process_edit_thread(
            self, request, parent_thread, thread, voting_enabled,
            voting_valid, formset_params=None):
        formset_params = formset_params or {}
        models = self.site.models
        right_model = self.site.core.right_model
        right_form = self.site.core.right_form
        adding = thread is None
        moderate = parent_thread.moderate_right(request.user)
        comment = None
        if thread and thread.first_comment:
            comments = models.Comment.objects.filter(
                id=thread.first_comment_id)
            if comments:
                comment = comments[0]
        formset_params['parent_thread'] = parent_thread
        form = forms.ThreadForm(
            models, thread, comment, voting_enabled, moderate,
            data=request.POST or None)

        formset = inlineformsets.get_formset(
            models.Thread, right_model, request.POST,
            base_form=right_form, extra=1, params=formset_params,
            instance=thread)
        if request.method == 'POST':
            form_valid = form.is_valid()
            if form_valid and voting_enabled:
                voting_valid = voting_valid or (
                    not form.cleaned_data['voting'])
            if form_valid and ((not voting_enabled) or voting_valid):
                access_type = int(form.cleaned_data['access_type'])
                free_access = (access_type <= models.THREAD_ACCESS_TYPE_OPEN)
                if free_access or formset.is_valid():
                    if not thread:
                        thread = models.Thread(
                            parent=parent_thread, room=False)
                    thread.title = form.cleaned_data['title']
                    if not thread.title:
                        thread.title = ''
                    thread.title = thread.title[:120]
                    thread.body = form.cleaned_data['body'][:255]
                    thread.plugin_id = parent_thread.plugin_id
                    if adding:
                        thread.user = request.user
                    thread.access_type = access_type
                    if moderate:
                        thread.important = form.cleaned_data['important']
                    thread.closed = form.cleaned_data['closed']
                    thread.save()
                    if not comment:
                        comment = models.Comment(parent=thread)
                    comment.title = thread.title
                    comment.body = form.cleaned_data['body']
                    if adding:
                        comment.user = thread.user
                    comment.plugin_id = parent_thread.plugin_id
                    if voting_enabled:
                        comment.voting = form.cleaned_data['voting']
                    comment.save()
                    if formset and not free_access:
                        if adding:
                            for form in formset:
                                if form.is_valid():
                                    right = form.save(commit=False)
                                    right.thread = thread
                                    right.save()
                        else:
                            formset.save()
                else:
                    thread = None
        else:
            thread = None
        return form, formset, thread, comment

    def delete_thread(self, user, thread_id, message):
        models = self.site.models
        success = 'error'
        error_text = ''
        redirect = ''
        text = ''
        thread = None
        try:
            thread_id = int(thread_id)
            thread = models.Thread.objects.select_for_update().get(
                id=thread_id)
        except:
            error_text = _('Thread not found %(post_id)s.') % {
                'post_id': thread_id}
        if thread:
            if not thread.edit_right(user):
                error_text = _(
                    'You have no rights to delete thread %(post_id)s.') % {
                        'post_id': thread_id}
            else:
                thread.deleted = True
                delete_mark = models.ThreadDeleteMark(
                    thread=thread, user=user, description=message)
                thread.save()
                delete_mark.save()
                if thread.parent:
                    redirect = thread.parent.get_absolute_url
                else:
                    redirect = self.reverse('index')
            success = 'success'
            text = _('Room successfully deleted!') if thread.room else _(
                'Thread successfully deleted!')
        return success, error_text, redirect, text

    def search_list(self, user, parent, **kwargs):
        queryset = self.models.Thread.objects.filter(
            plugin_id=self.site_id, deleted=False, parent=parent, **kwargs)
        thread_list = []
        for thread in queryset:
            thread.parent = parent
            if not thread.read_right(user):
                continue
            thread_list += [thread] + self.search_list(user, thread, **kwargs)
        return thread_list

    def expand_move_list(self, queryset, thread, user):
        thread_list = []
        for room in queryset:
            if (
                    not room.is_descendant_of(thread, include_self=True)) and \
                    room.write_right(user):
                thread_list += [room]
                if room.get_descendant_count():
                    subqueryset = room.get_children().filter(
                        room=True, deleted=False)
                    for subroom in subqueryset:
                        subroom.parent = room
                    thread_list += self.expand_move_list(
                        subqueryset, thread, user)
        return thread_list

    def move_list(self, thread, user):
        queryset = self.models.Thread.objects.filter(
            plugin_id=self.site_id, level=0, room=True, deleted=False)
        move_list = self.expand_move_list(queryset, thread, user)
        if user.is_superuser and thread.room:
            move_list = [None] + move_list
        return move_list

    def move_thread(self, thread, user, new_parent):
        if not thread.edit_right(user):
            raise http.Http404("no rights")
        if new_parent:
            if not new_parent.write_right(user):
                raise http.Http404("no rights")
        else:
            if not user.is_superuser:
                raise http.Http404("no rights")
        if new_parent not in self.move_list(thread, user):
            raise http.Http404("bad new parent")
        if new_parent and new_parent.is_descendant_of(
                thread, include_self=True):
            raise http.Http404("can`t move to a descendant")
        old_parent = thread.parent
        old_tree_id = thread.tree_id
        thread.parent = new_parent
        thread.save()
        if old_parent and ((not new_parent) or (
                old_parent.tree_id != new_parent.tree_id)):
            obj = self.models.Thread.objects.get(
                tree_id=old_parent.tree_id, parent=None)
            self.repair_thread_counters(obj, only_stats=True)
            obj.save()
        if new_parent:
            obj = self.models.Thread.objects.get(
                tree_id=new_parent.tree_id, parent=None)
            self.repair_thread_counters(obj, only_stats=True)
            obj.save()
        self.thread_on_move.send(
            thread, user=user, old_parent=old_parent, old_tree_id=old_tree_id)

    def repair_thread_counters(self, thread=None, only_stats=False):
        if not only_stats:
            if thread:
                self.models.Thread.objects.partial_rebuild(thread.tree_id)
            else:
                self.models.Thread.objects.rebuild()
        self._repair_thread_counters(thread)

    def _repair_thread_counters(self, thread=None):
        threads = self.models.Thread.objects.filter(
            parent=thread, deleted=False)
        for t in threads:
            if t.room:
                self._repair_thread_counters(t)
            self.thread_repair_counters.send(t)
            t.save()

    def init_core(self):
        self.thread_view_signal = dispatch.Signal(
            providing_args=["context", "user", "request"])
        self.threads_list_signal = dispatch.Signal(
            providing_args=["threads", "is_room"])
        self.thread_prepare_room_signal = dispatch.Signal(
            providing_args=["parent_thread", "threads", "user"])
        self.thread_prepare_room_group_signal = dispatch.Signal(
            providing_args=["user"])
        self.thread_before_edit = dispatch.Signal(
            providing_args=["thread", "context"])
        self.thread_after_edit = dispatch.Signal(
            providing_args=["thread", "context"])
        self.thread_on_move = dispatch.Signal(
            providing_args=["user", "old_parent", "old_tree_id"])
        self.thread_repair_counters = dispatch.Signal(providing_args=[])
        self.thread_on_create = dispatch.Signal(providing_args=['instance'])
        self.thread_on_update = dispatch.Signal(
            providing_args=["old_thread"])
        self.core['get_parent_thread'] = self.get_parent_thread
        self.core['prepare_room_list'] = self.prepare_room_list
        self.core['get_subthreads'] = self.get_subthreads
        self.core['process_edit_room'] = self.process_edit_room
        self.core['process_edit_thread'] = self.process_edit_thread
        self.core['delete_thread'] = self.delete_thread
        self.core['get_index'] = self.get_index
        self.core['room_descendants'] = self.room_descendants
        self.core['move_thread'] = self.move_thread
        self.core['thread_move_list'] = self.move_list
        self.core['Thread_rebuild'] = self.repair_thread_counters
        self.core['rebuild_tree'] = self.repair_thread_counters
        self.core['threads_search_list'] = self.search_list
        self.signals['thread_view'] = self.thread_view_signal
        self.signals['threads_list'] = self.threads_list_signal
        self.signals['thread_before_edit'] = self.thread_before_edit
        self.signals['thread_after_edit'] = self.thread_after_edit
        self.signals['thread_on_move'] = self.thread_on_move
        self.signals['thread_repair_counters'] = self.thread_repair_counters
        self.signals['thread_on_create'] = self.thread_on_create
        self.signals['thread_on_update'] = self.thread_on_update
        self.signals['thread_prepare_room'] = self.thread_prepare_room_signal
        self.signals['thread_prepare_room_group'] = \
            self.thread_prepare_room_group_signal
