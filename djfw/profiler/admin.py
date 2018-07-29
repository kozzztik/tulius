from django.contrib import admin

from . import models


class ProfilerMessageAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False


admin.site.register(models.ProfilerMessage, ProfilerMessageAdmin)
