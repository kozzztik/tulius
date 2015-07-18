from django.db import models
from djfw.bugtracker.models import Bug
from django.utils.translation import ugettext_lazy as _

class SiteUpdate(models.Model):
    class Meta:
        verbose_name = _('Site update')
        verbose_name_plural = _('Site updates')
        ordering = ['-id']
    revision = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('revision')
    )
    start_time = models.DateTimeField(
        auto_now_add=False,
        verbose_name=_('start time'),
    )
    end_time = models.DateTimeField(
        auto_now_add=False,
        null=True,
        blank=True,
        verbose_name=_('end time'),
    )
    @models.permalink
    def get_absolute_url(self):
        return ('bugs:site_updates', (), {  })

class SiteUpdateIssues(models.Model):
    class Meta:
        verbose_name = _('Site update')
        verbose_name_plural = _('Site updates')

    update = models.ForeignKey(
        SiteUpdate, 
        null=False,
        blank=False,
        related_name='issues', 
    )

    issue = models.ForeignKey(
        Bug, 
        null=False,
        blank=False,
        related_name='site_updates', 
    )
