from django.db.models.query_utils import Q
from django.utils import translation
from django.contrib import admin
from django import forms
from django.utils.translation import ugettext_lazy as _
from djfw.common.admin import CustomModelAdmin
from .models import TreePage

class TreepageForm(forms.ModelForm):
    url = forms.RegexField(label=_("URL"), max_length=100, regex=r'^[-\w/\.~]*/$',
        help_text = _("Example: '/about/contact/'. Make sure to have leading and trailing slashes."),
        error_message = _("This value must contain only letters, numbers, dots, underscores, dashes, slashes or tildes."))
    class Meta:
        model = TreePage
    
    def __init__(self, *args, **kwargs):
        super(TreepageForm, self).__init__(*args, **kwargs)
        language = translation.get_language()
        instance = None
        if 'instance' in kwargs:
            instance = kwargs['instance']
            language = instance.language
        field = self.fields['parent']
        field.queryset = field.queryset.filter(language = language)
        if instance:
            field.queryset = field.queryset.exclude(tree_id=instance.tree_id, lft__gte=instance.lft, rght__lte=instance.rght)
        
class TreePageAdmin(CustomModelAdmin):
    form = TreepageForm

    list_display = (
        'parent',
        'tree_unicode',
        'url',
        'title',
        'is_enabled',
    )
    list_display_links = (
        'tree_unicode',
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
    def queryset(self, request):
        lang = translation.get_language()
        query = Q(language=lang) | Q(language__isnull=True)
        return super(TreePageAdmin, self).queryset(request).filter(query)
_("Position")

admin.site.register(TreePage, TreePageAdmin)