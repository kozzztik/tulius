from django.conf import urls

from tulius.counters import views

app_name = 'tulius.counters'

urlpatterns = [
    urls.url(r'^$', views.CountersIndex.as_view(), name='index'),
    urls.url(r'^forum/$', views.ForumNums.as_view(), name='forum'),
    urls.url(r'^pm/$', views.PMCounters.as_view(), name='pm'),
]
