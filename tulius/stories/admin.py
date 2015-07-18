from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from django import forms
from .models import Genre, Story

class GenreForm(forms.ModelForm):
    class Meta:
        model = Genre
    
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
