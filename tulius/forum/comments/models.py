"""
Forum comment models for Tulius project
"""
from django import urls
import django.core.serializers.json
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from django.utils import html

from djfw.wysibb.templatetags import bbcodes
from tulius.forum.threads import models as thread_models
from tulius.forum.comments import signals


User = get_user_model()


class AbstractComment(models.Model):
    """
    Forum comment
    """
    class Meta:
        verbose_name = _('comment')
        verbose_name_plural = _('comments')
        ordering = ['id']
        abstract = True

    COMMENTS_ON_PAGE = 25

    objects = models.Manager()  # linters don't worry, be happy

    parent = models.ForeignKey(
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
    data = models.JSONField(
        default=dict,
        encoder=django.core.serializers.json.DjangoJSONEncoder)
    media = models.JSONField(
        default=dict,
        encoder=django.core.serializers.json.DjangoJSONEncoder)

    @property
    def page(self):
        return self.order_to_page(self.order)

    def __str__(self):
        return self.title[:40] if self.title else self.body[:40]

    def is_thread(self):
        return not self.order

    def get_absolute_url(self):
        return urls.reverse('forum_api:comment', kwargs={'pk': self.pk})

    def edit_right(self, user):
        if not user.is_authenticated:
            return False
        return (self.user_id == user.pk) or self.parent.moderate_right(user)

    def to_elastic_search(self, data):
        data['parent_id'] = self.parent_id
        data['parents_ids'] = (
            (self.parent.parents_ids or []) + [self.parent_id])
        data['user'] = {
            'id': self.user.pk,
            'title': str(self.user),
            'date_joined': self.user.date_joined,
            'sex': self.user.sex,
        }
        data['public'] = bool(
            (self.parent.rights.all or 0) & thread_models.ACCESS_READ)
        data['read_access'] = []
        for u, r in self.parent.rights:
            if r & thread_models.ACCESS_READ:
                data['read_access'].append(u)

    @classmethod
    def to_elastic_mapping(cls, fields):
        fields['parent_id'] = {'type': 'integer'}
        fields['parents_ids'] = {'type': 'integer'}
        fields['user'] = {'properties': {
            'id': {'type': 'integer'},
            'title': {'type': 'keyword'},
            'date_joined': {'type': 'date'},
            'sex': {'type': 'integer'},
        }}
        fields['public'] = {'type': 'boolean'}
        fields['read_access'] = {'type': 'integer'}

    @classmethod
    def order_to_page(cls, order):
        return int(order / cls.COMMENTS_ON_PAGE) + 1

    def to_json(self, user):
        data = {
            'id': self.pk,
            'thread': {
                'id': self.parent_id,
                'url': self.parent.get_absolute_url()
            },
            'page': self.page,
            'url': self.get_absolute_url() if self.pk else None,
            'title': html.escape(self.title),
            'body': bbcodes.bbcode(self.body),
            'user': self.user.to_json(detailed=True),
            'create_time': self.create_time,
            'edit_right': self.edit_right(user),
            'is_thread': self.is_thread(),
            'edit_time': self.edit_time,
            'editor': self.editor.to_json() if self.editor else None,
            'media': self.media,
            'reply_id': self.reply_id,
        }
        signals.to_json.send(
            self.__class__, comment=self, data=data, user=user)
        return data


class Comment(AbstractComment):
    pass


thread_models.AbstractThread.first_comment = thread_models.CounterField(
    'first_comment')
thread_models.AbstractThread.last_comment = thread_models.CounterField(
    'last_comment')
thread_models.AbstractThread.comments_count = thread_models.CounterField(
    'comments_count', default=0)
