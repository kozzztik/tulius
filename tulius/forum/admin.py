from .models import UploadedFile
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

_('forum')

admin.site.register(UploadedFile)
