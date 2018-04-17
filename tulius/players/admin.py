from django import forms
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .models import PlayerStar


_('players')


class PlayerStarForm(forms.ModelForm):
    class Meta:
        model = PlayerStar
        fields = '__all__'


class PlayerStarAdmin(admin.ModelAdmin):
    form = PlayerStarForm
    
    list_display = (
        'id',
        'games',
    )
    list_display_links = (
        'id',
    )
    list_editable = (
        'games',
    )


admin.site.register(PlayerStar, PlayerStarAdmin)
