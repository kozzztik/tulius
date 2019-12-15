import hashlib
import random
import re

from django import urls
from django.contrib import auth
from django.contrib import messages
from django.contrib.sites.models import Site
from django.contrib.sites.requests import RequestSite
from django.http import Http404, HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView, View, FormView

from .forms import LoginForm, ReLoginForm, RegistrationForm
from .models import RegistrationProfile


class Login(TemplateView):
    template_name = 'login/login.html'

    def get(self, request, *args, **kwargs):
        form = LoginForm(data=request.POST or None)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = auth.authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    auth.login(request, user)
                    messages.success(
                        request, _('You have successfully logged in'))
                    if 'next' in request.GET and request.GET['next']:
                        return HttpResponseRedirect(request.GET['next'])
                    if 'next' in request.POST and request.POST['next']:
                        return HttpResponseRedirect(request.POST['next'])
                    return HttpResponseRedirect('/')
                messages.error(request, _('This account is disabled'))
            else:
                messages.error(request, _('Invalid login/password pair'))
        return self.render_to_response({'form': form})

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)


class Logout(View):
    def get(self, request, *args, **kwargs):
        auth.logout(request)
        if 'next' in request.GET and request.GET['next']:
            return HttpResponseRedirect(request.GET['next'])
        if 'next' in request.POST and request.POST['next']:
            return HttpResponseRedirect(request.POST['next'])
        return HttpResponseRedirect('/')


class ReLogin(TemplateView):
    template_name = 'login/relogin.html'

    def get(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            raise Http404('Only for superuser')
        form = ReLoginForm(data=request.POST or None)
        if form.is_valid():
            user = form.cleaned_data['login_by_user']
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            if user.is_active:
                auth.login(request, user)
                messages.success(request, _('You have successfully logged in'))
            else:
                messages.error(request, _('This account is disabled'))
            return HttpResponseRedirect('/')
        return self.render_to_response({'form': form})

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)


class RegisterView(FormView):
    template_name = 'login/registration.haml'
    form_class = RegistrationForm
    success_url = urls.reverse_lazy('auth:registration_complete')

    def get_context_data(self, **kwargs):
        kwargs['form_submit_title'] = _('Sign up')
        return kwargs

    def form_valid(self, form):
        data = form.cleaned_data
        username, email, password = \
            data['username'], data['email'], data['password1']
        if Site._meta.installed:
            site = Site.objects.get_current()
        else:
            site = RequestSite(self.request)
        new_user = auth.get_user_model().objects.create_user(
            username, email, password)
        new_user.is_active = False
        new_user.save()

        salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
        if isinstance(username, str):
            username = username.encode('utf-8')
        activation_key = hashlib.sha1(salt+username).hexdigest()
        registration_profile = RegistrationProfile.objects.create(
            user=new_user, activation_key=activation_key)
        registration_profile.send_activation_email(site)
        return super(RegisterView, self).form_valid(form)


class ActivateView(TemplateView):
    template_name = 'login/activate.haml'
    SHA1_RE = re.compile('^[a-f0-9]{40}$')

    def get(self, request, *args, **kwargs):
        activation_key = kwargs.get('activation_key')
        profile = None
        if self.SHA1_RE.search(activation_key):
            try:
                profile = RegistrationProfile.objects.get(
                    activation_key=activation_key)
            except RegistrationProfile.DoesNotExist:
                pass
            if profile and not profile.activation_key_expired():
                user = profile.user
                user.is_active = True
                user.save()
                profile.activation_key = RegistrationProfile.ACTIVATED
                profile.save()
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                auth.login(request, user)
                messages.success(request, _('You have successfully logged in'))
                return HttpResponseRedirect(
                    urls.reverse('auth:registration_activation_complete'))
        return self.render_to_response(kwargs)
