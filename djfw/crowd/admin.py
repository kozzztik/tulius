from django.contrib import admin
from .models import User

class UserAdmin(admin.ModelAdmin):
    list_editable = (
    )

    def has_add_permission(self, request):
        return False

admin.site.register(User, UserAdmin)