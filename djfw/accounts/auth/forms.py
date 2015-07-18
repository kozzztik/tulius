from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from django import forms

class LoginForm(forms.Form):
	username = forms.CharField(max_length=100, label=_('username'))
	password = forms.CharField(widget=forms.PasswordInput, max_length=100, label=_('password'))
	
class ReloginForm(forms.Form):
	login_by_user = forms.ModelChoiceField(
        required = True,
        queryset = get_user_model().objects.all(),
        label = _(u'User'),
    )
	next_url = forms.CharField(widget=forms.HiddenInput)