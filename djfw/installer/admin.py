from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from .models import Backup, BackupCategory

_('installer')


class BackupAdmin(admin.ModelAdmin):
    list_filter = ['category']
    
    list_display = (
        'id',
        'category',
        'create_time',
        'file_size',
        'url'
    )
    list_display_links = (
        'create_time',
    )
    list_editable = (
    )

    def has_add_permission(self, request):
        return False


admin.site.register(Backup, BackupAdmin)


class BackupCategoryAdmin(admin.ModelAdmin):
    
    list_display = (
        'name',
        'verbose_name',
        'saved_backups',
        'enabled',
        'description',
    )
    list_display_links = (
        'name',
    )
    list_editable = (
        'verbose_name',
        'saved_backups',
        'enabled',
    )

    def has_add_permission(self, request):
        return False


admin.site.register(BackupCategory, BackupCategoryAdmin)
