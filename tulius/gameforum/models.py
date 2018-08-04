from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from tulius.forum.models import *
from tulius.stories.models import Variation, Role


class GameThreadRight(models.Model):
    """
    Game thread right
    """
    class Meta:
        verbose_name = _('game thread right')
        verbose_name_plural = _('game thread rights')
        unique_together = ('thread', 'role')

    thread = models.ForeignKey(
        Thread, models.PROTECT,
        null=False,
        blank=False,
        verbose_name=_(u'thread'),
        related_name='access_roles',
    )
    role = models.ForeignKey(
        Role, models.PROTECT,
        null=False,
        blank=False,
        verbose_name=_(u'role'),
        related_name='accessed_threads',
    )

    access_level = models.SmallIntegerField(
        default=0,
        verbose_name=_(u'access rights'),
        choices=THREAD_ACCESS_CHOICES,
    )


class Trustmark(models.Model):
    """
    TrustMark
    """
    class Meta:
        verbose_name = _('trust mark')
        verbose_name_plural = _('trust marks')
        unique_together = ('variation', 'user', 'role')

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, models.PROTECT,
        null=False,
        blank=False,
        verbose_name=_(u'user'),
        related_name='trust_marks',
    )

    variation = models.ForeignKey(
        Variation, models.PROTECT,
        null=False,
        blank=False,
        verbose_name=_(u'variation'),
        related_name='trust_marks',
    )

    role = models.ForeignKey(
        Role, models.PROTECT,
        null=False,
        blank=False,
        verbose_name=_(u'role'),
        related_name='trust_marks',
    )

    value = models.SmallIntegerField(
        null=False,
        blank=False,
        verbose_name=_(u'value'),
    )
