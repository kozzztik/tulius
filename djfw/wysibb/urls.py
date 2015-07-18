from django.conf.urls import patterns, url
from .views import upload_file, upload_image

urlpatterns = patterns('',
    url(r'^upload_file/$', upload_file, name='upload_file'),
    url(r'^upload_image/$', upload_image, name='upload_image'),
)