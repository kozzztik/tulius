from django import urls

from tulius.login import views


app_name = 'tulius.login'

urlpatterns = [
    urls.re_path(r'^login/$', views.Login.as_view(), name='login'),
    urls.re_path(
        r'^login_choose/$',
        views.TemplateView.as_view(template_name='login/choose.haml'),
        name='login_choose'),
    urls.re_path(r'^logout/$', views.Logout.as_view(), name='logout'),
    urls.re_path(r'^relogin/$', views.ReLogin.as_view(), name='relogin'),
    urls.re_path(
        r'^activate/complete/$',
        views.TemplateView.as_view(
            template_name='login/activation_complete.haml'),
        name='registration_activation_complete'),
    # Activation keys get matched by \w+ instead of the more specific
    #  [a-fA-F0-9]{40} because a bad activation key should still get to the
    # view;
    #  that way it can return a sensible "invalid key" message instead of a
    #  confusing 404.
    urls.re_path(
        r'^registration/activate/(?P<activation_key>\w+)/$',
        views.ActivateView.as_view(),
        name='registration_activate'),
    urls.re_path(
        r'^registration/register/$',
        views.RegisterView.as_view(),
        name='registration_register'),
    urls.re_path(
        r'^registration/register/complete/$',
        views.TemplateView.as_view(
            template_name='login/registration_complete.haml'),
        name='registration_complete'),
]
