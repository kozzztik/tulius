from django.conf.urls import patterns, include, url
from .views import vk_success_auth, vk_auth_reddirect

urlpatterns = patterns('',
    url(r'^login_vk_oauth/$', vk_auth_reddirect, name='auth_oauth'),
    url(r'^login_vk_success/$', vk_success_auth, name='auth_success'),

)