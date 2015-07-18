from django.conf.urls import patterns, url
from .views import *

urlpatterns = patterns('',
    url(r'^download/(?P<object_id>\d+)/$', download_backup, name='backup'),
)