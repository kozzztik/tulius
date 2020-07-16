from django.views import generic
from django.conf.urls import url

from tulius.forum.threads.plugin import ThreadsPlugin


class Index(generic.TemplateView):
    template_name = 'base_vue.html'


class GameThreadsPlugin(ThreadsPlugin):
    def get_urls(self):
        return [
            url(r'^$', Index.as_view(), name='index'),
            url(
                r'^(?P<variation_id>\d+)/',
                Index.as_view(), name='game_forum_variation'),
            url(
                r'^(?P<variation_id>\d+)/room/(?P<pk>\d+)/',
                Index.as_view(), name='room_new'),
            url(
                r'^(?P<variation_id>\d+)/thread/(?P<pk>\d+)/',
                Index.as_view(), name='thread_new'),
            url(
                r'^room/(?P<parent_id>\d+)/$',
                Index.as_view(), name='room'),
            url(
                r'^add_room/$',
                Index.as_view(), name='add_room'),
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
