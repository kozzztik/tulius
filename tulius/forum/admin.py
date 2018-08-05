from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from tulius.forum import models


_('forum')

admin.site.register(models.UploadedFile)
