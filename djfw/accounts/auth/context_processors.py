from django.utils.timezone import now
from .forms import ReloginForm

def relogin(request):
	return {
		'relogin_form': ReloginForm(initial={'next_url': request.path}),
		'request': request
	}