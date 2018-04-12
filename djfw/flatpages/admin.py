from django import forms
from django.contrib import admin
from .models import FlatPage
from django.utils.translation import ugettext_lazy as _
from djfw.common.admin import CustomModelAdmin


class FlatpageForm(forms.ModelForm):
    url = forms.RegexField(label=_("URL"), max_length=100, regex=r'^[-\w/\.~]*/$',
                           help_text=_("Example: '/about/contact/'. Make sure to have leading and trailing slashes."),
                           error_message=_("This value must contain only letters, numbers, dots, underscores, "
                                           "dashes, slashes or tildes."))

    class Meta:
        model = FlatPage


class FlatPageAdmin(CustomModelAdmin):
    form = FlatpageForm

    list_display = (
        '__unicode__',
        'url',
        'title',
        'is_enabled',
    )
    list_display_links = (
        '__unicode__',
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

admin.site.register(FlatPage, FlatPageAdmin)
