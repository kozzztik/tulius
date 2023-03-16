from django import urls

from tulius.vk import views


app_name = 'tulius.vk'

urlpatterns = [
    urls.re_path(
        r'^login_vk_oauth/$', views.vk_auth_reddirect, name='auth_oauth'),
    urls.re_path(
        r'^login_vk_success/$', views.vk_success_auth, name='auth_success'),
]
