from django.conf.urls import url
from .views import *

app_name = 'djfw.installer'

urlpatterns = [
    url(r'^download/(?P<object_id>\d+)/$', download_backup, name='backup'),
]
