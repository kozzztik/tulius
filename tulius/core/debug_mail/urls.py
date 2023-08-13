from django import urls

from tulius.core.debug_mail import views

app_name = 'debug_mail'

urlpatterns = [
    urls.re_path(r'^$', views.RecipientsAPI.as_view(), name='mail_recipients'),
    urls.re_path(
        r'^(?P<email>[^\/]+)/$', views.MailboxAPI.as_view(), name='mail_box'),
    urls.re_path(
        r'^(?P<email>[^\/]+)/(?P<pk>[\d.]+)/$',
        views.MailAPI.as_view(), name='mail_content'),
]
