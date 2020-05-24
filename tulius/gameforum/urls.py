from django.conf import urls

from tulius.gameforum import views


app_name = 'tulius.gameforum'

urlpatterns = [
    urls.url(
        r'^thread_redirrect/(?P<pk>\d+)/$',
        views.RedirrectAPI.as_view(), name='thread_redirect'),

    urls.url(
        r'^variation/(?P<pk>\d+)/$',
        views.VariationAPI.as_view(), name='variation'),

]
