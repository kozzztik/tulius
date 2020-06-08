from django.conf import urls

from tulius.gameforum import views
from tulius.gameforum import threads
from tulius.gameforum import other
from tulius.gameforum import online_status


app_name = 'tulius.gameforum'

urlpatterns = [
    urls.url(
        r'^thread_redirrect/(?P<pk>\d+)/$',
        views.RedirrectAPI.as_view(), name='thread_redirect'),
    urls.url(
        r'^variation/(?P<variation_id>\d+)/$',
        views.VariationAPI.as_view(), name='variation'),
    urls.url(
        r'^variation/(?P<variation_id>\d+)/thread/(?P<pk>\d+)/$',
        threads.ThreadAPI.as_view(), name='thread'),
    urls.url(
        r'^variation/(?P<variation_id>\d+)/thread/(?P<pk>\d+)/read_mark/$',
        other.ReadmarkAPI.as_view(), name='thread_readmark'),
    urls.url(
        r'^variation/(?P<variation_id>\d+)/thread/(?P<pk>\d+)/online_status/$',
        online_status.OnlineStatusAPI.as_view(), name='online_status'),
]
