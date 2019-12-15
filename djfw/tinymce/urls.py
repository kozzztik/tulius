from django.conf.urls import url

from djfw.tinymce import views

app_name = 'djfw.tinymce'

urlpatterns = [
    url(r'^$', views.Smiles.as_view(), name='index'),
    url(r'^emotions/emotions.htm$', views.Smiles.as_view(), name='smiles'),
    url(
        r'^uploaded_files/$',
        views.Uploaded_files.as_view(),
        name='uploaded_files'),
    url(r'^upload_file/$', views.Upload_file.as_view(), name='upload_file'),
]
