from django.conf.urls import *
from djfw.flatpages.views import *

urlpatterns = patterns('',
	url(r'^(?P<url>.*)$', flatpage, name='flatpage'),
	url(r'^flatpages/$', FlatpagesList.as_view(), template_name='flatpages/list.haml', name='list'),
)
