from django import forms
from django.utils.translation import ugettext_lazy as _
from tulius.stories.models import Role


class SearchForm(forms.Form):
    text = forms.CharField(label=_("search"))


class ExtendedSearchForm(forms.Form):
    thread = forms.ChoiceField(label=_("place"), required=False)
    roles = forms.ModelMultipleChoiceField(
        label=_("from characters"),
        required=False,
        queryset=Role.objects.all())
    not_roles = forms.ModelMultipleChoiceField(
        label=_("not from characters"),
        required=False,
        queryset=Role.objects.all())
    date_from = forms.CharField(label=_("from date"), required=False)
    date_to = forms.CharField(label=_("to date"), required=False)
    text = forms.CharField(label=_("text"), required=False)
    
    def __init__(self, roles, threads, *args, **kwargs):
        super(ExtendedSearchForm, self).__init__(*args, **kwargs)
        self.fields['roles'].queryset = roles
        self.fields['not_roles'].queryset = roles
        self.fields['thread'].choices = threads
