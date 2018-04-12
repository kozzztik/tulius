from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from django import forms
import re


class LoginForm(forms.Form):
    username = forms.CharField(max_length=100, label=_('username'))
    password = forms.CharField(widget=forms.PasswordInput, max_length=100, label=_('password'))


class ReLoginForm(forms.Form):
    login_by_user = forms.ModelChoiceField(
        required=True,
        queryset=get_user_model().objects.all(),
        label=_(u'User'),
    )
    next_url = forms.CharField(widget=forms.HiddenInput)


attrs_dict = {'class': 'required'}


class RegistrationForm(forms.Form):
    username = forms.RegexField(re.compile(r"^[\w\s-]+$", re.UNICODE),
                                max_length=30,
                                widget=forms.TextInput(attrs=attrs_dict),
                                label=_("Username"),
                                error_messages={'invalid': _("This value may contain only letters, "
                                                             "numbers and @/./+/-/_ characters.")})
    email = forms.EmailField(widget=forms.TextInput(attrs=dict(attrs_dict, maxlength=75)),
                             label=_("E-mail"))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
                                label=_("Password"))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
                                label=_("Password (again)"))

    def clean_username(self):
        existing = get_user_model().objects.filter(username__iexact=self.cleaned_data['username'])
        if existing.exists():
            raise forms.ValidationError(_("A user with that username already exists."))
        else:
            return self.cleaned_data['username']

    def clean(self):
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError(_("The two password fields didn't match."))
        return self.cleaned_data
