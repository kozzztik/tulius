from django import urls

from djfw.tinymce import views

app_name = 'djfw.tinymce'

urlpatterns = [
    urls.re_path(r'^$', views.Smiles.as_view(), name='index'),
    urls.re_path(
        r'^emotions/emotions.htm$', views.Smiles.as_view(), name='smiles'),
    urls.re_path(
        r'^uploaded_files/$',
        views.Uploaded_files.as_view(),
        name='uploaded_files'),
    urls.re_path(
        r'^upload_file/$', views.Upload_file.as_view(), name='upload_file'),
]
