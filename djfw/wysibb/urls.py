from django.conf.urls import url
from djfw.wysibb import views


app_name = 'djfw.wysibb'

urlpatterns = [
    url(r'^upload_file/$', views.upload_file, name='upload_file'),
    url(r'^upload_image/$', views.upload_image, name='upload_image'),
    url(r'^options/$', views.wysibb_options, name='options'),
]
