from django.utils.translation import ugettext_lazy as _
from django.db import models

class Setting(models.Model):
    """
    Advanced setting
    """
    class Meta:
        verbose_name = _('setting')
        verbose_name_plural = _('settings')
        unique_together = ('folder', 'name')
        
    folder = models.CharField(
        max_length=50, 
        blank=False,
        null=False,
        verbose_name=_('folder')
    )

    name = models.CharField(
        max_length=50, 
        default = '',
        blank=True,
        verbose_name=_('name')
    )
    
    value = models.CharField(
        max_length=255, 
        blank=True,
        null=True,
        verbose_name=_('name')
    )
    def __unicode__(self):
        return "[%s] %s : %s" % (self.folder, self.name, self.value)