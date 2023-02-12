from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from tulius.forum import models


_('forum')

admin.site.register(models.UploadedFile)
