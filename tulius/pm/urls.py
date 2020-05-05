from django.conf import urls

from tulius.pm import views


app_name = 'tulius.pm'

urlpatterns = [
    urls.url(
        r'^messages/$',
        views.PlayerMessagesView.as_view(),
        name='messages'),
    urls.url(
        r'^user/(?P<pk>\d+)/$',
        views.PlayerSendMessageView.as_view(),
        name='to_user'),
]
