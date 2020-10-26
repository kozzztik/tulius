from django.utils.translation import gettext_lazy as _
from django import forms
from django.contrib import auth

from tulius.models import User


class NotificationForm(forms.Form):
    enabled = forms.BooleanField(
        required=False,
        label=_(u'enabled'),
    )


class ProfileSettingsForm(forms.models.ModelForm):
    class Meta:
        model = User
        fields = (
            'sex', 'icq', 'skype', 'show_played_games',
            'show_played_characters', 'game_inline',
            'animation_speed')


class PersonalSettingsForm(forms.models.ModelForm):
    class Meta:
        model = User
        fields = (
            'hide_trustmarks', 'show_online_status', 'compact_text',
            'signature')


class ChangeEmailForm(forms.Form):
    email = forms.EmailField(
        required=False,
        label=_(u'Email'),
    )
    new_pass = forms.CharField(
        required=False,
        label=_(u'New password'),
        widget=forms.PasswordInput
    )
    repeat_pass = forms.CharField(
        required=False,
        label=_(u'Repeat password'),
        widget=forms.PasswordInput
    )
    current_pass = forms.CharField(
        required=False,
        label=_(u'Current password'),
        widget=forms.PasswordInput
    )

    def clean_current_pass(self):
        current_pass = self.cleaned_data['current_pass']
        email = self.cleaned_data['email']
        new_pass = self.cleaned_data['new_pass']
        if (email != self.user.email) or new_pass:
            if not current_pass:
                raise forms.ValidationError(
                    _("You need current password to change this settings"))
            user = auth.authenticate(
                username=self.user.username, password=current_pass)
            if not user:
                raise forms.ValidationError(_("Invalid password"))
            if new_pass:
                self.change_pass = True
            if email != self.user.email:
                self.change_email = True
        return current_pass

    def clean_repeat_pass(self):
        new_pass = self.cleaned_data['new_pass']
        repeat_pass = self.cleaned_data['repeat_pass']
        if new_pass or repeat_pass:
            if new_pass != repeat_pass:
                raise forms.ValidationError(_("Passwords don`t match"))
        return repeat_pass

    def __init__(self, user, data):
        self.user = user
        self.change_email = False
        self.change_pass = False
        super().__init__(data=data or None, initial={'email': user.email})
