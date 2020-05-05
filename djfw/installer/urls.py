from django.conf.urls import url

from djfw.installer import views

app_name = 'djfw.installer'

urlpatterns = [
    url(
        r'^download/(?P<object_id>\d+)/$',
        views.download_backup,
        name='backup'),
]
