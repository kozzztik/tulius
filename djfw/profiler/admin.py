from django.contrib import admin
from .models import ProfilerMessage 

class ProfilerMessageAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False
    
admin.site.register(ProfilerMessage, ProfilerMessageAdmin)