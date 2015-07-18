from django.utils.translation import ugettext_lazy as _
from django.db import models

class Emotion(models.Model):
    """
    Editor emotion
    """
    class Meta:
        verbose_name = _('emotion')
        verbose_name_plural = _('emotions')
    
    name = models.CharField(
        max_length=500, 
        unique=False, 
        verbose_name=_('name')
    )
    
    text = models.CharField(
        max_length=500, 
        unique=False, 
        verbose_name=_('text')
    )
    
    filename = models.CharField(
        max_length=500, 
        unique=False, 
        verbose_name=_('filename')
    )

    def __unicode__(self):
        return self.name
    