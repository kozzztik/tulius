from django.conf.urls import patterns, url
from .views import autocomplete_user, get_autocomplete

urlpatterns = patterns('',  
    url('user', autocomplete_user, name='user'),
    url(r'^(?P<token>[\w-]+)/$', get_autocomplete, name='autocomplete'),
)  