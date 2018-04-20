from django.conf.urls import url
from .views import *

app_name = 'tulius.counters'

urlpatterns = [
    url(r'^$', CountersIndex.as_view(), name='index'),
    url(r'^forum/$', ForumNums.as_view(), name='forum'),
    url(r'^pm/$', PMCounters.as_view(), name='pm'),
]
