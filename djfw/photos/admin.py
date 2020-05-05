from django import forms
from django.contrib import admin

from .models import PhotoAlbum, Photo


class PhotoAlbumForm(forms.ModelForm):
    class Meta:
        model = PhotoAlbum
        widgets = {
            'description': forms.Textarea(attrs={'class': 'mceNoEditor'}),
        }
        fields = '__all__'


class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ('title', 'description', )
        widgets = {
            'description': forms.Textarea(attrs={'class': 'mceNoEditor'}),
        }


class PhotoInline(admin.TabularInline):
    model = Photo
    template = 'photos/admin_photos.haml'
    form = PhotoForm
    extra = 0


class PhotoAlbumAdmin(admin.ModelAdmin):
    form = PhotoAlbumForm
    inlines = [PhotoInline, ]

    list_display = (
        'preview_image_url',
        'title',
        'enabled',
        'photo_count',
        'tags',
    )
    list_display_links = (
        'preview_image_url',
    )
    list_editable = (
        'title',
        'enabled',
    )


admin.site.register(PhotoAlbum, PhotoAlbumAdmin)
