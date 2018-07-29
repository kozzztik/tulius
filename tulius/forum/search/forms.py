from django.utils.translation import ugettext_lazy as _
from django import forms

from tulius.models import User
from .widgets import AutocompleteUsersWidget


class SearchForm(forms.Form):
    text = forms.CharField(label=_("search"))


class ExtendedSearchForm(forms.Form):
    thread = forms.ChoiceField(label=_("place"), required=False)
    users = forms.ModelMultipleChoiceField(
        label=_("from users"),
        required=False,
        queryset=User.objects.all(),
        widget=AutocompleteUsersWidget())
    not_users = forms.ModelMultipleChoiceField(
        label=_("not from users"),
        required=False,
        queryset=User.objects.all(),
        widget=AutocompleteUsersWidget())
    date_from = forms.CharField(label=_("from date"), required=False)
    date_to = forms.CharField(label=_("to date"), required=False)
    text = forms.CharField(label=_("text"), required=False)
    
    def __init__(self, threads, *args, **kwargs):
        super(ExtendedSearchForm, self).__init__(*args, **kwargs)
        self.fields['thread'].choices = threads
