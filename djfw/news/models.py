from django import urls
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.utils import translation

from djfw.common.models import AbstractBaseModel


class NewsItem(AbstractBaseModel):
    class Meta(AbstractBaseModel.Meta):
        verbose_name = _('news item')
        verbose_name_plural = _('news items')
        ordering = ['-published_at']

    caption = models.CharField(
        max_length=300,
        default='',
        blank=False,
        null=False,
        verbose_name=_('caption')
    )
    announcement = models.TextField(
        default='',
        blank=True,
        null=True,
        verbose_name=_('announcement')
    )
    full_text = models.TextField(
        default='',
        blank=True,
        null=True,
        verbose_name=_('full text')
    )
    is_published = models.BooleanField(
        default=False,
        verbose_name=_('is published')
    )
    published_at = models.DateTimeField(
        verbose_name=_('published at')
    )
    language = models.CharField(
        verbose_name=_('language'),
        max_length=10,
        null=False,
        blank=False,
        editable=False
    )

    def __str__(self):
        return str(self.caption)

    def get_absolute_url(self):
        return urls.reverse('news:detail', kwargs={'pk': self.pk})

    def save(
            self, force_insert=False, force_update=False, using=None,
            update_fields=None):
        if not self.language:
            self.language = translation.get_language()
        super().save(
            force_insert=force_insert, force_update=force_update,
            using=using, update_fields=update_fields)
