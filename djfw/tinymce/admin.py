from django.contrib import admin
from django import forms
from django.utils.translation import ugettext_lazy as _
from .models import FileUpload

class FileUploadForm(forms.ModelForm):
    class Meta:
        model = FileUpload

class FileUploadAdmin(admin.ModelAdmin):
    form = FileUploadForm

    list_display = (
        'preview_image_url',
        'user',
        'filename',
        'get_absolute_url',
        'mime',
        'file_size',
    )
    list_display_links = (
        'preview_image_url',
    )
    list_editable = (
        'filename',
    )
    
    def has_add_permission(self, request):
        return False
    
admin.site.register(FileUpload, FileUploadAdmin)