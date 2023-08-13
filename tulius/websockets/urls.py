from django import urls

from tulius.websockets import views


app_name = 'tulius.websockets'


urlpatterns = [
    urls.re_path(r'^$', views.web_socket_view, name='ws'),
    urls.re_path(
        r'^old/$', views.web_socket_view, {'json_format': False}, name='old'),
]
