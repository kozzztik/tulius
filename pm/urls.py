from django.conf.urls import patterns, url
from pm.views import *

urlpatterns = patterns('',

	url(r'^$',
		index,
		name='index'
	),
	url(r'^history/(?P<another_user_id>\d+)/$',
		history,
		name='history'
	),
	url(r'^inbox/$',
		inbox,
		name='inbox'
	),
	url(r'^outbox/$',
		outbox,
		name='outbox'
	),
	url(r'^message/(?P<message_id>\d+)$',
		message_details,
		name='message_details'
	),
	url(r'^message/create/(?P<another_user_id>\d+)/$',
		message_create,
		name='message_create'
	),
	
)