from django.utils.translation import gettext_lazy as _
from django.db import models


class UpdatedAndCreatedDatesMixin(models.Model):
    class Meta:
        abstract = True
        ordering = ['-updated_at']

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('updated at'),
        # editable=False,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('created at'),
        # editable=False,
    )


class SortableMixin(models.Model):
    class Meta:
        abstract = True
        ordering = ['position']
    position = models.PositiveSmallIntegerField(
        _("Position"), blank=True, null=True)


class AbstractBaseModel(UpdatedAndCreatedDatesMixin, SortableMixin):
    class Meta(UpdatedAndCreatedDatesMixin.Meta, SortableMixin.Meta):
        abstract = True
        ordering = ['position']


class AbstractStatusModel(AbstractBaseModel):
    class Meta(AbstractBaseModel.Meta):
        verbose_name = _('status')
        verbose_name_plural = _('statuses')
        abstract = True

    name = models.CharField(
        max_length=200,
        default='',
        blank=False,
        null=False,
        verbose_name=_('name')
    )

    def __unicode__(self):
        return '#%s. %s' % (self.pk, self.name,)


class AbstractDescribedStatusModel(AbstractStatusModel):
    class Meta(AbstractBaseModel.Meta):
        verbose_name = _('described status')
        verbose_name_plural = _('described statuses')
        abstract = True

    description = models.TextField(
        null=True,
        blank=True,
        default='',
        verbose_name=_(u'Описание')
    )


class AbstractMessage(AbstractBaseModel):
    class Meta(AbstractBaseModel.Meta):
        verbose_name = _('message')
        verbose_name_plural = _('messages')
        abstract = True

    title = models.CharField(
        max_length=200,
        unique=False,
        verbose_name=_('title')
    )
    body = models.TextField(
        null=True,
        blank=True,
        default='',
        verbose_name=_('body')
    )

    def __unicode__(self):
        return '#%s. %s' % (self.pk, self.title,)


class AbstractQuestion(AbstractBaseModel):
    class Meta(AbstractBaseModel.Meta):
        verbose_name = _('question')
        verbose_name_plural = _('questions')
        abstract = True

    body = models.TextField(
        default='',
        verbose_name=_(u'body')
    )

    def __unicode__(self):
        return u'%s' % self.body
