from django.conf.urls import url
from .core import ThreadsCorePlugin
from . import views


class ThreadsPlugin(ThreadsCorePlugin):
    def thread_url(self, thread):
        return self.reverse('room' if thread.room else 'thread', thread.id)

    def thread_move(self, thread):
        return self.reverse('thread_move', thread.id)

    def thread_move_confirm(self, thread, new_parent):
        if new_parent:
            return self.reverse(
                'thread_move_confirm', thread.id, new_parent.id)
        return self.reverse('thread_move_confirm', thread.id)

    def index_url(self):
        return self.reverse('index')

    def add_root_room_url(self):
        return self.reverse('add_room')

    def thread_edit_url(self, thread):
        return self.reverse('edit_thread', thread.id)

    def get_add_room_url(self, thread):
        return self.reverse('add_room', thread.id)

    def get_add_thread_url(self, thread):
        return self.reverse('add_thread', thread.id)

    def get_comments_page_url(self, thread):
        return self.reverse('comments_page', thread.id)

    def init_core(self):
        super(ThreadsPlugin, self).init_core()
        self.urlizer['thread'] = self.thread_url
        self.urlizer['index'] = self.index_url
        self.urlizer['add_root_room'] = self.add_root_room_url
        self.templates['thread_move_select'] = \
            'forum/threads/move_select.haml'
        self.templates['thread_move_confirm'] = \
            'forum/threads/move_confirm.haml'
        self.core['Thread_get_edit_url'] = self.thread_edit_url
        self.core['move_thread_confirm_url'] = self.thread_move_confirm
        self.urlizer['Thread_get_absolute_url'] = self.thread_url
        self.urlizer['Thread_get_add_room_url'] = self.get_add_room_url
        self.urlizer['Thread_get_add_thread_url'] = self.get_add_thread_url
        self.urlizer['Thread_get_comments_page_url'] = \
            self.get_comments_page_url
        self.urlizer['Thread_get_move_url'] = self.thread_move

    def get_urls(self):
        return [
            url(r'^$', views.Index.as_view(), name='index'),
            url(
                r'^room/(?P<parent_id>\d+)/$',
                views.Index.as_view(), name='room'),
            url(r'^add_room/$', views.Index.as_view(), name='add_room'),
            url(
                r'^add_room/(?P<parent_id>\d+)/$',
                views.Index.as_view(), name='add_room'),
            url(
                r'^add_thread/(?P<parent_id>\d+)/$',
                views.Index.as_view(), name='add_thread'),
            url(
                r'^edit_thread/(?P<thread_id>\d+)/$',
                views.Index.as_view(), name='edit_thread'),
            url(
                r'^thread/(?P<parent_id>\d+)/$',
                views.Index.as_view(), name='thread'),
            url(
                r'^search/(?P<parent_id>\d+)/$',
                views.Index.as_view(), name='thread_search'),
            url(
                r'^thread/(?P<parent_id>\d+)/move/$',
                views.MoveThreadSelect.as_view(plugin=self),
                name='thread_move'),
            url(
                r'^thread/(?P<parent_id>\d+)/move/(?P<thread_id>\d+)/$',
                views.MoveThreadConfirm.as_view(plugin=self),
                name='thread_move_confirm'),
            url(r'^thread/(?P<parent_id>\d+)/move/root/$',
                views.MoveThreadConfirm.as_view(plugin=self),
                name='thread_move_confirm'),
        ]
