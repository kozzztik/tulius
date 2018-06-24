from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from .models import Notification

_('events')

admin.site.register(Notification)
