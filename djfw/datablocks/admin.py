from django.contrib import admin
from django import forms
from django.utils.translation import ugettext_lazy as _
from .models import DataBlock

class DataBlockForm(forms.ModelForm):
    class Meta:
        model = DataBlock
        widgets = {
            'urls': forms.Textarea(attrs={'class': 'mceNoEditor'}),
            'exclude_urls': forms.Textarea(attrs={'class': 'mceNoEditor'}),
        }
        
class DataBlockAdmin(admin.ModelAdmin):
    form = DataBlockForm

    list_display = (
        'name',
        'full_text',
        'urls',
        'exclude_urls',
    )
    list_display_links = (
        'name',
    )
    list_editable = (
    )
    def queryset(self, request):
        qs = self.model._default_manager.languaged()
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs
    
admin.site.register(DataBlock, DataBlockAdmin)