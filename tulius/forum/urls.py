from django.conf import urls

from tulius.forum.threads import api as threads_api
from tulius.forum.collapse_threads import views as collapse_views

app_name = 'tulius.forum'

urlpatterns = [
    urls.url(r'^$', threads_api.IndexView.as_view(), name='index'),
    urls.url(
        r'^collapse/$',
        collapse_views.CollapseAPIList.as_view(), name='collapse_list'),
    urls.url(
        r'^collapse/(?P<pk>\d+)$',
        collapse_views.CollapseAPISave.as_view(), name='collapse_save'),
    urls.url(
        r'^thread/(?P<pk>\d+)/$',
        threads_api.ThreadView.as_view(), name='thread'),
]
