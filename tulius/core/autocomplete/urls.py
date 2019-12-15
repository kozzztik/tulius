from django.conf.urls import url

from tulius.core.autocomplete import views

app_name = 'tulius.core.autocomplete'

urlpatterns = [
    url('user', views.autocomplete_user, name='user'),
    url(r'^(?P<token>[\w-]+)/$', views.get_autocomplete, name='autocomplete'),
]
