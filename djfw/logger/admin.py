from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from . import models

_('logger')


class LogMessageAdmin(admin.ModelAdmin):
    list_filter = ['level']

    list_display = (
        'create_time',
        'level',
        'logger_name',
        'body',
    )
    list_display_links = (
        'create_time',
    )
    list_editable = (
    )

    def has_add_permission(self, request):
        return False


admin.site.register(models.LogMessage, LogMessageAdmin)


class ExceptionMessageAdmin(admin.ModelAdmin):
    list_display = (
        'create_time',
        'user_link',
        'classname',
        'title',
        'path_link',
    )
    list_display_links = (
        'create_time',
    )
    list_editable = (
    )

    def has_add_permission(self, request):
        return False


admin.site.register(models.ExceptionMessage, ExceptionMessageAdmin)
