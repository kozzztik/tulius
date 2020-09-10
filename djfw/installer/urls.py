from django.conf import urls

from djfw.installer import views

app_name = 'djfw.installer'

urlpatterns = [
    urls.re_path(
        r'^download/(?P<object_id>\d+)/$',
        views.download_backup,
        name='backup'),
]
