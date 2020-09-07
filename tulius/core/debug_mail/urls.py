from django.conf import urls

from tulius.core.debug_mail import views

app_name = 'debug_mail'

urlpatterns = [
    urls.url(r'^$', views.RecipientsAPI.as_view(), name='mail_recipients'),
    urls.url(
        r'^(?P<email>[^\/]+)/$', views.MailboxAPI.as_view(), name='mail_box'),
    urls.url(
        r'^(?P<email>[^\/]+)/(?P<pk>[\d.]+)/$',
        views.MailAPI.as_view(), name='mail_content'),
]
