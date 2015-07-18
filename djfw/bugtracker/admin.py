from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from .models import JiraUser, BugtrackerSetting, BugVersion, Bug
from django.contrib.admin.options import csrf_protect_m
from .admin_views import SettingsView, AdminProxyView
from functools import update_wrapper
from django.conf.urls import patterns, url
from .views import BugAdminViews, VersionsAdminViews

_('bugtracker')

class JiraUserAdmin(admin.ModelAdmin):
    actions = None
    
    list_display = (
        'small_image_link',
        'user',
        'active',
    )
    list_display_links = (
        'small_image_link',
    )
    list_editable = (
        'user',
        'active',
    )

    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
admin.site.register(JiraUser, JiraUserAdmin)

class MyBaseAdmin(admin.ModelAdmin):
    def wrap_view(self, view):
        def wrapper(*args, **kwargs):
            return self.admin_site.admin_view(view)(*args, **kwargs)
        return update_wrapper(wrapper, view)

class BugtrackerSettingAdmin(MyBaseAdmin):
    actions = None
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False

    def get_urls(self):
        urls = patterns('', url(r'^settings/$', self.wrap_view(self.settings_view), name='bugtracker_settings'), )
        return urls + super(BugtrackerSettingAdmin, self).get_urls()
    
    @csrf_protect_m
    def settings_view(self, request, extra_context=None):
        return SettingsView.as_view(model=self.model)(request)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['title'] = _('Settings')
        return super(BugtrackerSettingAdmin, self).changelist_view(request, extra_context)

admin.site.register(BugtrackerSetting, BugtrackerSettingAdmin)

from django.contrib.admin.util import unquote
    
class BugVersionAdmin(MyBaseAdmin):
    actions = None
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def get_urls(self):
        views = BugAdminViews(decorator=self.wrap_view)
        return views.get_urls() + super(BugVersionAdmin, self).get_urls()
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['title'] = _('Versions')
        return super(BugVersionAdmin, self).changelist_view(request, extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        obj = self.get_object(request, unquote(object_id))
        extra_context['title'] = _('Issues of version %s') % unicode(obj)
        return super(BugVersionAdmin, self).change_view(request, object_id, form_url, extra_context)
    
admin.site.register(BugVersion, BugVersionAdmin)

class BugAdmin(MyBaseAdmin):
    actions = None
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False

    def get_urls(self):
        views = BugAdminViews(decorator=self.wrap_view)
        urls = patterns('', 
                        url(r'^list/$', self.wrap_view(AdminProxyView.as_view(modeladmin=self)), name='bugtracker_list'),)
        return urls + views.get_urls() + super(BugAdmin, self).get_urls()

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        obj = self.get_object(request, unquote(object_id))
        extra_context['title'] = obj.key
        return super(BugAdmin, self).change_view(request, object_id, form_url=form_url, extra_context=extra_context)
    
admin.site.register(Bug, BugAdmin)