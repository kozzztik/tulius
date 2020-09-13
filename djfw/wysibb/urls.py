from django.conf import urls

from djfw.wysibb import views


app_name = 'djfw.wysibb'

urlpatterns = [
    urls.re_path(r'^upload_file/$', views.upload_file, name='upload_file'),
    urls.re_path(r'^upload_image/$', views.upload_image, name='upload_image'),
]
