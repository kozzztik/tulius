from django.conf.urls import patterns, url
from .views import view_sync_all, found_bug

urlpatterns = patterns ('',
    url(r'^found_bug/exception/(?P<exception_id>\d+)/$', found_bug, name='found_bug_with_exception'),
    url(r'^found_bug/$', found_bug, name='found_bug'),
    url(r'^sync/all/$', view_sync_all, name='sync_all'),
)