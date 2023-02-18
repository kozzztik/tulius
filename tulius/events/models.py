from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class Notification(models.Model):
    """
    Notification
    """
    class Meta:
        verbose_name = _('notification')
        verbose_name_plural = _('notifications')
        ordering = ['order']

    objects = models.Manager()  # linters don't worry, be happy

    code_name = models.CharField(
        max_length=40,
        default='',
        blank=False,
        null=False,
        unique=True,
        verbose_name=_(u'code name')
    )
    order = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name=_(u'order'),
    )
    name = models.CharField(
        max_length=100,
        default='',
        blank=True,
        null=True,
        verbose_name=_(u'name')
    )
    description = models.CharField(
        max_length=250,
        default='',
        blank=True,
        null=True,
        verbose_name=_(u'description')
    )
    header_template = models.TextField(
        default='',
        blank=True,
        verbose_name=_(u'header template')
    )
    body_template = models.TextField(
        default='',
        blank=True,
        verbose_name=_(u'body template')
    )

    def __str__(self):
        return str(self.name or self.code_name)


class UserNotification(models.Model):
    """
    User notification
    """
    class Meta:
        verbose_name = _('user notification')
        verbose_name_plural = _('user notifications')

    objects = models.Manager()  # linters don't worry, be happy

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, models.PROTECT,
        null=False,
        blank=False,
        verbose_name=_(u'user'),
        related_name='notifications',
    )

    notification = models.ForeignKey(
        Notification, models.PROTECT,
        null=False,
        blank=False,
        verbose_name=_(u'notification'),
        related_name='users',
    )

    enabled = models.BooleanField(
        default=True,
        verbose_name=_(u'enabled')
    )

    def __str__(self):
        return "%s - %s" % (
            self.user, self.notification.name or self.notification.code_name)


class IncomeMail(models.Model):
    sender = models.CharField(
        max_length=200,
        blank=False,
    )
    recipient = models.CharField(
        max_length=200,
        blank=False,
    )
    sender_mail = models.CharField(
        max_length=200,
        blank=False,
    )
    recipient_mail = models.CharField(
        max_length=200,
        blank=False,
    )
    headers = models.TextField(
        blank=False,
    )
    body = models.TextField(
        default='',
        blank=True,
    )
