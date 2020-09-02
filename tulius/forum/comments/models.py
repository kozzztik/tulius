"""
Forum comment models for Tulius project
"""
import jsonfield
from django import urls
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from mptt import models as mptt_models

from tulius.forum.threads import models as thread_models

User = get_user_model()


def default_json():
    return {}


class AbstractComment(models.Model):
    """
    Forum comment
    """
    class Meta:
        verbose_name = _('comment')
        verbose_name_plural = _('comments')
        ordering = ['id']
        abstract = True

    objects = models.Manager()  # linters don't worry, be happy

    parent = mptt_models.TreeForeignKey(
        thread_models.Thread, models.PROTECT,
        null=False,
        blank=False,
        related_name='comments',
        verbose_name=_('thread')
    )
    title = models.CharField(
        max_length=255,
        unique=False,
        verbose_name=_('title')
    )

    body = models.TextField(
        verbose_name=_('body')
    )

    user = models.ForeignKey(
        User, models.PROTECT,
        null=False,
        blank=False,
        related_name='%(app_label)s',
        verbose_name=_('author')
    )
    editor = models.ForeignKey(
        User, models.PROTECT,
        null=True,
        blank=True,
        related_name='%(app_label)s_edited',
        verbose_name=_('edited by')
    )
    create_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('created at'),
    )
    edit_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('edited at'),
    )
    reply = models.ForeignKey(
        'self', models.PROTECT,
        null=True,
        blank=True,
        related_name='answers',
        verbose_name=_('reply to')
    )
    deleted = models.BooleanField(
        default=False,
        verbose_name=_(u'deleted')
    )
    order = models.IntegerField(
        null=False,
        blank=False,
        verbose_name=_(u'order'),
    )
    data = jsonfield.JSONField(default=default_json)
    media = jsonfield.JSONField(default=default_json)

    def __str__(self):
        return self.title[:40] if self.title else self.body[:40]

    def is_thread(self):
        return not self.order

    def get_absolute_url(self):
        return urls.reverse('forum_api:comment', kwargs={'pk': self.pk})


class Comment(AbstractComment):
    pass


def get_param(param, thread, user_id, superuser=False):
    data = thread.data.get(param)
    if not data:
        return None
    if superuser:
        return data['su']
    if user_id and str(user_id) in data['users']:
        return data['users'][str(user_id)]
    return data['all']
