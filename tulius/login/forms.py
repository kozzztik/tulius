import re

from django import forms
from django.contrib import auth
from django.utils.translation import gettext_lazy as _


user_model = auth.get_user_model()


class LoginForm(forms.Form):
    username = forms.CharField(max_length=100, label=_('username'))
    password = forms.CharField(
        widget=forms.PasswordInput, max_length=100, label=_('password'))


class ReLoginForm(forms.Form):
    login_by_user = forms.ModelChoiceField(
        required=True,
        queryset=user_model.objects.all(),
        label=_(u'User'),
        widget=user_model.autocomplete_widget
    )


attrs_dict = {'class': 'required'}


class RegistrationForm(forms.Form):
    username = forms.RegexField(
        re.compile(r"^[\w\s-]+$", re.UNICODE),
        max_length=30,
        widget=forms.TextInput(attrs=attrs_dict),
        label=_("Username"),
        error_messages={
            'invalid': _(
                "This value may contain only letters, "
                "numbers and @/./+/-/_ characters.")})
    email = forms.EmailField(
        widget=forms.TextInput(attrs=dict(attrs_dict, maxlength=75)),
        label=_("E-mail"))
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
        label=_("Password"))
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
        label=_("Password (again)"))

    def clean_username(self):
        existing = user_model.objects.filter(
            username__iexact=self.cleaned_data['username'])
        if existing.exists():
            raise forms.ValidationError(
                _("A user with that username already exists."))
        return self.cleaned_data['username']

    def clean(self):
        data = self.cleaned_data
        if 'password1' in data and 'password2' in data:
            if data['password1'] != data['password2']:
                raise forms.ValidationError(
                    _("The two password fields didn't match."))
        return data
