from pm.models import *

def unread_messages(request):
	if request.user.is_anonymous():
		return {
			'unread_messages': [],
			'request': request
		}
	return {
		'unread_messages': PrivateMessage.objects.filter(receiver=request.user, is_read=False),
		'request': request
	}