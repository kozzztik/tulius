from django import urls
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from tulius.forum.threads import models as thread_models

User = get_user_model()


THREAD_ACCESS_CHOICES = (
    (
        thread_models.ACCESS_READ + thread_models.ACCESS_WRITE,
        _('read and write rights')),
    (
        thread_models.ACCESS_READ,
        _('read right')),
    (
        thread_models.ACCESS_MODERATOR,
        _('read, write and moderate')),
    (
        thread_models.ACCESS_WRITE,
        _('write only right')),
    (
        thread_models.ACCESS_READ + thread_models.ACCESS_MODERATE,
        _('read and moderate right(no write)')),
)


class ThreadAccessRight(models.Model):
    """
    Right to access forum thread
    """
    class Meta:
        verbose_name = _('thread access right')
        verbose_name_plural = _('threads access rights')
        unique_together = ('thread', 'user')

    objects = models.Manager()  # linters don't worry, be happy

    thread = models.ForeignKey(
        thread_models.Thread, models.PROTECT,
        null=False,
        blank=False,
        related_name='granted_rights',
        verbose_name=_('thread')
    )
    user: User = models.ForeignKey(
        User, models.PROTECT,
        null=False,
        blank=False,
        related_name='forum_threads_rights',
        verbose_name=_('user')
    )
    access_level = models.SmallIntegerField(
        default=thread_models.ACCESS_READ + thread_models.ACCESS_WRITE,
        verbose_name=_('access rights'),
        choices=THREAD_ACCESS_CHOICES,
    )

    def get_absolute_url(self):
        return urls.reverse(
            'forum_api:thread_right',
            kwargs={'pk': self.thread_id, 'right_id': self.pk})

    def to_json(self):
        return {
            'id': self.pk,
            'user': {
                'id': self.user.pk,
                'title': self.user.username,
            },
            'access_level': self.access_level,
            'url': self.get_absolute_url(),
        }
