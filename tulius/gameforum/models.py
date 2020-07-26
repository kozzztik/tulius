from django import urls
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from tulius.forum.rights import models as rights
from tulius.gameforum.threads import models as thread_models
from tulius.stories import models as stories


class GameThreadRight(models.Model):
    """
    Game thread right
    """
    class Meta:
        verbose_name = _('game thread right')
        verbose_name_plural = _('game thread rights')
        unique_together = ('thread', 'role')

    thread: thread_models.Thread = models.ForeignKey(
        thread_models.Thread, models.PROTECT,
        null=False,
        blank=False,
        verbose_name=_(u'thread'),
        related_name='access_roles',
    )
    role: stories.Role = models.ForeignKey(
        stories.Role, models.PROTECT,
        null=False,
        blank=False,
        verbose_name=_(u'role'),
        related_name='accessed_threads',
    )

    access_level = models.SmallIntegerField(
        default=rights.THREAD_ACCESS_READ + rights.THREAD_ACCESS_WRITE,
        verbose_name=_(u'access rights'),
        choices=rights.THREAD_ACCESS_CHOICES,
    )

    def get_absolute_url(self):
        return urls.reverse(
            'game_forum_api:thread_right', kwargs={
                'pk': self.thread_id,
                'right_id': self.pk,
                'variation_id': self.thread.variation_id
            })

    def to_json(self):
        return {
            'id': self.pk,
            'user': {
                'id': self.role.pk,
                'title': self.role.name,
            },
            'access_level': self.access_level,
            'url': self.get_absolute_url(),
        }


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
        stories.Variation, models.PROTECT,
        null=False,
        blank=False,
        verbose_name=_(u'variation'),
        related_name='trust_marks',
    )

    role = models.ForeignKey(
        stories.Role, models.PROTECT,
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
