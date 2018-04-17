from django import forms
from django.contrib import admin

from .models import Genre


class GenreForm(forms.ModelForm):
    class Meta:
        model = Genre
        fields = '__all__'


class GenreAdmin(admin.ModelAdmin):
    form = GenreForm
    
    list_display = (
        'id',
        'name',
        'stories_list',
    )
    list_display_links = (
        'id',
    )
    list_editable = (
        'name',
    )


admin.site.register(Genre, GenreAdmin)
