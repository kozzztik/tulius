from django import forms
from django.contrib import admin

from .models import Smile, UploadedImage, UploadedFile


class SmileForm(forms.ModelForm):
    class Meta:
        model = Smile
        fields = '__all__'


class SmileAdmin(admin.ModelAdmin):
    form = SmileForm

    list_display = (
        'preview_image',
        'name',
        'text',
    )
    list_display_links = (
        'preview_image',
    )
    list_editable = (
        'name',
        'text',
    )


admin.site.register(Smile, SmileAdmin)


class UploadedImageForm(forms.ModelForm):
    class Meta:
        model = UploadedImage
        exclude = ('image', 'thumb')


class UploadedImageAdmin(admin.ModelAdmin):
    form = UploadedImageForm

    list_display = (
        'preview_image',
        'user',
        'created_at',
        'file_size_formated',
    )
    
    list_display_links = (
    )
    
    list_editable = (
    )
    
    def has_add_permission(self, request):
        return False


admin.site.register(UploadedImage, UploadedImageAdmin)


class UploadedFileForm(forms.ModelForm):
    class Meta:
        model = UploadedFile
        exclude = ('body',)


class UploadedFileAdmin(admin.ModelAdmin):
    form = UploadedFileForm

    list_display = (
        'filename_link',
        'user',
        'created_at',
        'mime',
        'file_size_formated',
    )
    
    list_display_links = (
    )
    
    list_editable = (
    )

    def has_add_permission(self, request):
        return False


admin.site.register(UploadedFile, UploadedFileAdmin)
