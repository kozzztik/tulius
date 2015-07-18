# -*- coding: utf-8 -*-
from django.utils import translation
from django.contrib import admin
from .models import NewsItem
from djfw.common.admin import CustomModelAdmin
from djfw.common.admin.actions import export_as_csv

class NewsItemAdmin(CustomModelAdmin):
    
    list_display    = (
        'id',
        '__unicode__',
        'caption',
        'is_published',
        'published_at',
        'created_at',
        'updated_at',
    )
    list_editable = (
        'caption',
        'is_published',
    )    
    list_filter = (
        'is_published',
    )
    list_per_page = 50
    
    search_fields = (
        'id',
        'caption',
        'announcement',
        'full_text'
    )
    def queryset(self, request):
        return super(NewsItemAdmin, self).queryset(request).filter(language=translation.get_language())
    
    def make_published(self, request, queryset):
        queryset.update(is_published=True)
        
    make_published.short_description = u'publish selected news'
    
    def make_unpublished(self, request, queryset):
        queryset.update(is_published=False)
        
    make_unpublished.short_description = u'unpublish selected news'
    
    actions = [
        export_as_csv,
        make_published,
        make_unpublished,
    ]

admin.site.register(NewsItem, NewsItemAdmin)