from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from django import forms
from .models import PlayerStar

_('players')

class PlayerStarForm(forms.ModelForm):
    class Meta:
        model = PlayerStar
    
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