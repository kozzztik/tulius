from django.utils.translation import ugettext_lazy as _, ugettext as __
from django.views.generic import TemplateView, View
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.http import Http404, HttpResponseRedirect
from .forms import LoginForm, ReloginForm

class Login(TemplateView):
	template_name='accounts/auth/login.haml'
	
	def get(self, request, *args, **kwargs):
		form = LoginForm(data=request.POST or None)
		if form.is_valid():
			username = form.cleaned_data['username']
			password = form.cleaned_data['password']
			user = authenticate(username=username, password=password)
			if user is not None:
				if user.is_active:
					auth_login(request, user)
					messages.success(request, _('You have successfully logged in'))
					if 'next' in request.GET and request.GET['next']:
						return HttpResponseRedirect(request.GET['next'])
					elif 'next' in request.POST and request.POST['next']:
						return HttpResponseRedirect(request.POST['next'])
					else:
						return HttpResponseRedirect('/')
				else:
					messages.error(request, _('This account is disabled'))
			else:
				messages.error(request, _('Invalid login/password pair'))
		return self.render_to_response({'form': form})
	
	def post(self, request, *args, **kwargs):
		return self.get(request, *args, **kwargs)
	
class Logout(View):
	def get(self, request, *args, **kwargs):
		auth_logout(request)
		if 'next' in request.GET and request.GET['next']:
			return HttpResponseRedirect(request.GET['next'])
		elif 'next' in request.POST and request.POST['next']:
			return HttpResponseRedirect(request.POST['next'])
		else:
			return HttpResponseRedirect('/')
	
class Relogin(View):
	def get(self, request, *args, **kwargs):
		if not request.user.is_superuser:
			raise Http404('Only for superuser')
		form = ReloginForm(data=request.POST or None)
		if form.is_valid():
			user = form.cleaned_data['login_by_user']
			user.backend = 'django.contrib.auth.backends.ModelBackend'
			next_url = form.cleaned_data['next_url']
			if user.is_active:
				auth_login(request, user)
				messages.success(request, _('You have successfully logged in'))
			else:
				messages.error(request, _('This account is disabled'))
			if next_url:
				HttpResponseRedirect(next_url)
		else:
			messages.success(request, _('Form invalid'))
		return HttpResponseRedirect('/')
	def post(self, request, *args, **kwargs):
		return self.get(request, *args, **kwargs)