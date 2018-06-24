from django.conf.urls import url
from .views import *

app_name = 'tulius.pm'

urlpatterns = [
    url(
        r'^messages/$',
        PlayerMessagesView.as_view(),
        name='messages'),
    url(
        r'^user/(?P<pk>\d+)/$',
        PlayerSendMessageView.as_view(),
        name='to_user'),
]
