from .models import Setting
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

_('adv_settings')

admin.site.register(Setting)