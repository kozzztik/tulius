from django.conf.urls import patterns, url
from .views import *

urlpatterns = patterns('',
    url(r'^$', Smiles.as_view(), name='index'),
    url(r'^emotions/emotions.htm$', Smiles.as_view(), name='smiles'),
    url(r'^uploaded_files/$', Uploaded_files.as_view(), name='uploaded_files'),
    url(r'^upload_file/$', Upload_file.as_view(), name='upload_file'),
)