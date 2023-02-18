from django import urls

from tulius.counters import views

app_name = 'tulius.counters'

urlpatterns = [
    urls.re_path(r'^$', views.CountersIndex.as_view(), name='index'),
    urls.re_path(r'^pm/$', views.PMCounters.as_view(), name='pm'),
]
