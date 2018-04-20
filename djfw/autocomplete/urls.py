from django.conf.urls import url
from .views import autocomplete_user, get_autocomplete

app_name = 'djfw.autocomplete'

urlpatterns = [
    url('user', autocomplete_user, name='user'),
    url(r'^(?P<token>[\w-]+)/$', get_autocomplete, name='autocomplete'),
]
