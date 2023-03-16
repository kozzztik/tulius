from django.db import models
from django.utils.translation import gettext_lazy as _
from djfw.common.models import AbstractBaseModel


class FlatPage(AbstractBaseModel):
    url = models.CharField(_('URL'), max_length=100, db_index=True)
    title = models.CharField(_('title'), max_length=200)
    content = models.TextField(_('content'), blank=True)
    is_enabled = models.BooleanField(_('is enabled'))
    show_on_home = models.BooleanField(_('show on home'))

    class Meta(AbstractBaseModel.Meta):
        verbose_name = _('flat page')
        verbose_name_plural = _('flat pages')
        ordering = ('position',)

    def __str__(self):
        return '%s -- %s' % (self.url, self.title)

    def get_absolute_url(self):
        return self.url
