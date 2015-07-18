from django.conf.urls import patterns, include, url
from .views import *

urlpatterns = patterns('',
    url(r'^$', CountersIndex.as_view(), name='index'),
    url(r'^forum/$', ForumNums.as_view(), name='forum'),
    url(r'^pm/$', PMCounters.as_view(), name='pm'),
)
