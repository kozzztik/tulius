from django.conf import urls

from tulius.gameforum import views
from tulius.gameforum import threads


app_name = 'tulius.gameforum'

urlpatterns = [
    urls.url(
        r'^thread_redirrect/(?P<pk>\d+)/$',
        views.RedirrectAPI.as_view(), name='thread_redirect'),

    urls.url(
        r'^variation/(?P<pk>\d+)/$',
        views.VariationAPI.as_view(), name='variation'),
    urls.url(
        r'^variation/(?P<variation_id>\d+)/thread/(?P<pk>\d+)/$',
        threads.ThreadAPI.as_view(), name='thread'),

]
