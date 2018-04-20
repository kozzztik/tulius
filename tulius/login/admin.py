from django.contrib import admin
from django.contrib.sites.requests import RequestSite
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _

from .models import RegistrationProfile


class RegistrationAdmin(admin.ModelAdmin):
    actions = ['activate_users', 'resend_activation_email']
    list_display = ('user', 'activation_key', 'activation_key_expired')
    raw_id_fields = ['user']
    search_fields = ('user__username', 'user__first_name', 'user__last_name')

    def activate_users(self, request, queryset):
        for profile in queryset:
            user = profile.user
            user.is_active = True
            user.save()
            profile.activation_key = RegistrationProfile.ACTIVATED
            profile.save()
    activate_users.short_description = _("Activate users")

    def resend_activation_email(self, request, queryset):
        if Site._meta.installed:
            site = Site.objects.get_current()
        else:
            site = RequestSite(request)

        for profile in queryset:
            if not profile.activation_key_expired():
                profile.send_activation_email(site)
    resend_activation_email.short_description = _("Re-send activation emails")


admin.site.register(RegistrationProfile, RegistrationAdmin)
