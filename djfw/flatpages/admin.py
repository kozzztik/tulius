from django import forms
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from djfw.common import admin as common_admin
from djfw.flatpages import models


class FlatpageForm(forms.ModelForm):
    url = forms.RegexField(
        label=_("URL"), max_length=100, regex=r'^[-\w/\.~]*/$',
        help_text=_(
            "Example: '/about/contact/'. "
            "Make sure to have leading and trailing slashes."),
        error_messages={
            'invalid': _(
                "This value must contain only letters, numbers, dots, "
                "underscores, dashes, slashes or tildes.")}
    )

    class Meta:
        model = models.FlatPage
        fields = '__all__'


class FlatPageAdmin(common_admin.CustomModelAdmin):
    form = FlatpageForm

    list_display = (
        '__str__',
        'url',
        'title',
        'is_enabled',
    )
    list_display_links = (
        '__str__',
    )
    list_editable = (
        'url',
        'title',
        'is_enabled',
    )
    list_filter = (
    )
    search_fields = (
        'url',
        'title',
    )
    date_hierarchy = None


admin.site.register(models.FlatPage, FlatPageAdmin)
