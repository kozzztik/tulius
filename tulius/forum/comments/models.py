"""
Forum engine models for Tulius project
"""
import jsonfield
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
    likes = models.IntegerField(
        null=False,
        blank=False,
        default=0,
        verbose_name=_(u'likes'),
    )
    page = models.IntegerField(
        null=False,
        blank=False,
        default=0,
        verbose_name=_(u'page'),
    )

    data = jsonfield.JSONField(default=default_json)
    media = jsonfield.JSONField(default=default_json)

    def __str__(self):
        return self.title[:40] if self.title else self.body[:40]

    def is_thread(self):
        return self.pk == self.parent.first_comment_id


class Comment(AbstractComment):
    parent = mptt_models.TreeForeignKey(
        thread_models.Thread, models.PROTECT,
        null=False,
        blank=False,
        related_name='comments',
        verbose_name=_('thread')
    )
