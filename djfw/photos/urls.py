from django.conf.urls import patterns, url
from .views import upload_file

urlpatterns = patterns ('',
    url(r'^upload/(?P<album_id>\d+)/$', upload_file, name='upload'),
)