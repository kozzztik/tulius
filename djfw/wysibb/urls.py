from django.conf.urls import url
from .views import upload_file, upload_image


app_name = 'djfw.wysibb'

urlpatterns = [
    url(r'^upload_file/$', upload_file, name='upload_file'),
    url(r'^upload_image/$', upload_image, name='upload_image'),
]
