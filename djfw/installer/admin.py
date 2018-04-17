from django.contrib import admin
from django.contrib.admin.utils import unquote
from django.core.exceptions import PermissionDenied
from django.utils.translation import ugettext_lazy as _
from .models import Backup, BackupCategory, MaintenanceLog
from .views import AddMaintainceView, ChangeMaintainceView
from django.utils import timezone

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


class MaintenanceLogAdmin(admin.ModelAdmin):
    
    list_display = (
        'id',
        'revision',
        'start_time',
        'end_time',
        'state',
        'comment'
    )
    list_display_links = (
        'id',
    )
    list_editable = (
    )
    
    def finish_manual_maintaince(self, request, queryset):
        for obj in queryset:
            if not obj.end_time:
                obj.end_time = timezone.now()
                obj.state = MaintenanceLog.STATE_SUCCESS
                obj.status = _('Finished manually')
                obj.save()
        return None
    finish_manual_maintaince.short_description = _("Manual finish maintaince")
    
    actions = [finish_manual_maintaince]
    
    def add_view(self, request, form_url='', extra_context=None):
        if not self.has_add_permission(request):
            raise PermissionDenied
        view = AddMaintainceView.as_view(
            modeladmin=self, extra_context=extra_context)
        return view(request)
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        obj = self.get_object(request, unquote(object_id))
        if not self.has_change_permission(request, obj):
            raise PermissionDenied
        view = ChangeMaintainceView.as_view(
            modeladmin=self, extra_context=extra_context, obj=obj)
        return view(request)


admin.site.register(MaintenanceLog, MaintenanceLogAdmin)
