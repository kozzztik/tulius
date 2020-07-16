from django.conf.urls import url
from django.views import generic

from .core import ThreadsCorePlugin


class Index(generic.TemplateView):
    template_name = 'base_vue.html'


class ThreadsPlugin(ThreadsCorePlugin):
    def thread_url(self, thread):
        return self.reverse('room' if thread.room else 'thread', thread.id)

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
        self.core['Thread_get_edit_url'] = self.thread_edit_url
        self.urlizer['Thread_get_absolute_url'] = self.thread_url
        self.urlizer['Thread_get_add_room_url'] = self.get_add_room_url
        self.urlizer['Thread_get_add_thread_url'] = self.get_add_thread_url
        self.urlizer['Thread_get_comments_page_url'] = \
            self.get_comments_page_url

    def get_urls(self):
        return [
            url(r'^$', Index.as_view(), name='index'),
            url(
                r'^room/(?P<parent_id>\d+)/$',
                Index.as_view(), name='room'),
            url(r'^add_room/$', Index.as_view(), name='add_room'),
            url(
                r'^add_room/(?P<parent_id>\d+)/$',
                Index.as_view(), name='add_room'),
            url(
                r'^add_thread/(?P<parent_id>\d+)/$',
                Index.as_view(), name='add_thread'),
            url(
                r'^edit_thread/(?P<thread_id>\d+)/$',
                Index.as_view(), name='edit_thread'),
            url(
                r'^thread/(?P<parent_id>\d+)/$',
                Index.as_view(), name='thread'),
            url(
                r'^search/(?P<parent_id>\d+)/$',
                Index.as_view(), name='search'),
            url(
                r'^extended_search/(?P<pk>\d+)/$',
                Index.as_view(), name='extended_search'),
        ]
