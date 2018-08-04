from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefUserAdmin
from django.contrib.auth import forms as auth_forms
from django.utils.translation import ugettext_lazy as _

from .models import User


class UserChangeForm(auth_forms.UserChangeForm):
    class Meta:
        model = User
        fields = '__all__'


class UserCreationForm(auth_forms.UserCreationForm):
    class Meta:
        model = User
        fields = '__all__'


class UserAdmin(DefUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Forum info'), {'fields': ('avatar', 'rank', 'signature')}),
        (_('Private'), {'fields': ('sex', 'icq', 'skype')}),
        (_('Settings'), {'fields': (
            'show_played_games', 'show_played_characters',
            'show_online_status', 'hide_trustmarks')}),
    )
    list_display = ('username', 'email', 'is_active',)
    search_fields = ('username', 'email')

    form = UserChangeForm
    add_form = UserCreationForm


admin.site.register(User, UserAdmin)
