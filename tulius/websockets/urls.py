from django.conf import urls

from tulius.websockets import views


app_name = 'tulius.websockets'


urlpatterns = [
    urls.re_path(r'^$', views.web_socket_view),
]
