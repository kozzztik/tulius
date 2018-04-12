from django.conf.urls import patterns, include, url
from views import *


urlpatterns = patterns('',
                       url(r'^login/$', Login.as_view(), name='login'),
                       url(r'^login_choose/$',
                           TemplateView.as_view(template_name='login/choose.haml'),
                           name='login_choose'),
                       url(r'^logout/$', Logout.as_view(), name='logout'),
                       url(r'^relogin/$', ReLogin.as_view(), name='relogin'),
                       url(r'^activate/complete/$',
                           TemplateView.as_view(template_name='login/activation_complete.haml'),
                           name='registration_activation_complete'),
                       # Activation keys get matched by \w+ instead of the more specific
                       #  [a-fA-F0-9]{40} because a bad activation key should still get to the view;
                       #  that way it can return a sensible "invalid key" message instead of a
                       #  confusing 404.
                       url(r'^registration/activate/(?P<activation_key>\w+)/$',
                           ActivateView.as_view(),
                           name='registration_activate'),
                       url(r'^registration/register/$', RegisterView.as_view(), name='registration_register'),
                       url(r'^registration/register/complete/$',
                           TemplateView.as_view(template_name='login/registration_complete.haml'),
                           name='registration_complete'),
                       )
