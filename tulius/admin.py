from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from .models import User
from django.contrib.auth.admin import UserAdmin as DefUserAdmin
from django.contrib.auth.forms import UserChangeForm as DefUserChangeForm, UserCreationForm as DefCreateForm

class UserChangeForm(DefUserChangeForm):
    class Meta:
        model = User

class UserCreationForm(DefCreateForm):
    class Meta:
        model = User

class UserAdmin(DefUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Forum info'), {'fields': ('avatar', 'rank', 'signature')}),
        (_('Private'), {'fields': ('sex', 'icq', 'skype')}),
        (_('Settings'), {'fields': ('show_played_games', 'show_played_characters', 'show_online_status', 'hide_trustmarks')}),
    )
    list_display = ('username', 'email', 'is_active',)
    search_fields = ('username', 'email')
    
    form = UserChangeForm
    add_form = UserCreationForm
    
admin.site.register(User, UserAdmin)
