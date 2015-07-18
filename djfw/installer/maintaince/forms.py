from django.utils.translation import ugettext_lazy as _
from django import forms

class RepoPasswordForm(forms.Form):
    realm = forms.CharField(
        max_length=255,
        label = _(u'Auth realm'),
        required=False,
        widget= forms.TextInput()
    )
    username = forms.CharField(
        max_length=255,
        label = _(u'Username'),
        required=True,
        widget= forms.TextInput()
    )
    password = forms.CharField(
        max_length=255,
        label = _(u'Password'),
        required=True,
        widget= forms.PasswordInput()
    )

class RepoRevisionForm(forms.Form):
    revision = forms.ChoiceField(
        choices=(),
        label = _(u'Revision'),
        required=True,
    )
    def __init__(self, choices, *args, **kwargs):
        super(RepoRevisionForm, self).__init__(*args, **kwargs)
        self.fields['revision'].choices = choices