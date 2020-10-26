from django.conf import urls

from tulius.pm import views


app_name = 'tulius.pm'

urlpatterns = [
    urls.re_path(
        r'^messages/$',
        views.PlayerMessagesView.as_view(),
        name='messages'),
    urls.re_path(
        r'^user/(?P<pk>\d+)/$',
        views.PlayerSendMessageView.as_view(),
        name='to_user'),
]
