from django.conf.urls import patterns, include, url
from djfw.accounts.auth.views import *

urlpatterns = patterns('',
	url(r'^login/$', Login.as_view(), name='login'),
	url(r'^logout/$', Logout.as_view(), name='logout'),
	url(r'^relogin/$', Relogin.as_view(), name='relogin'),
)