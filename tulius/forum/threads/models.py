"""
Forum engine base Thread entity
"""
import jsonfield
from django import urls
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from mptt import models as mptt_models


User = get_user_model()

THREAD_ACCESS_TYPE_NOT_SET = 0
THREAD_ACCESS_TYPE_OPEN = 1
THREAD_ACCESS_TYPE_NO_WRITE = 2
THREAD_ACCESS_TYPE_NO_READ = 3

THREAD_ACCESS_TYPE_CHOICES = (
    (THREAD_ACCESS_TYPE_NOT_SET, _(u'access not set')),
    (THREAD_ACCESS_TYPE_OPEN, _(u'free access')),
    (THREAD_ACCESS_TYPE_NO_WRITE, _(u'read only access')),
    (THREAD_ACCESS_TYPE_NO_READ, _(u'private(no access)')),
)

ACCESS_READ = 1
ACCESS_WRITE = 2
ACCESS_MODERATE = 4
ACCESS_EDIT = 8

ACCESS_OWN = ACCESS_READ + ACCESS_WRITE + ACCESS_EDIT

default_rights = {
    THREAD_ACCESS_TYPE_NO_READ: 0,
    THREAD_ACCESS_TYPE_NO_WRITE: ACCESS_READ,
    THREAD_ACCESS_TYPE_OPEN: ACCESS_READ + ACCESS_WRITE,
}


class ThreadManager(mptt_models.TreeManager):
    pass


def default_json():
    return {}


class AbstractThread(mptt_models.MPTTModel):
    """
    Forum thread
    """
    class Meta:
        verbose_name = _('thread')
        verbose_name_plural = _('threads')
        ordering = ['id']
        abstract = True

    objects = ThreadManager()

    title = models.CharField(
        max_length=255,
        unique=False,
        verbose_name=_('title')
    )
    body = models.TextField(verbose_name=_('body'))
    parent = mptt_models.TreeForeignKey(
        'self', models.PROTECT,
        null=True, blank=True,
        related_name='children',
        verbose_name=_('parent thread')
    )
    room = models.BooleanField(
        default=False,
        verbose_name=_(u'room')
    )
    user = models.ForeignKey(
        User, models.PROTECT,
        related_name='%(app_label)s',
        verbose_name=_('author')
    )
    access_type = models.SmallIntegerField(
        default=0,
        verbose_name=_(u'access type'),
        choices=THREAD_ACCESS_TYPE_CHOICES,
    )
    create_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('created at'),
    )
    closed = models.BooleanField(
        default=False,
        verbose_name=_(u'closed')
    )
    important = models.BooleanField(
        default=False,
        verbose_name=_(u'important')
    )
    deleted = models.BooleanField(
        default=False,
        verbose_name=_(u'deleted')
    )
    protected_threads = models.SmallIntegerField(
        default=0,
        verbose_name=_(u'protected threads')
    )
    first_comment_id = models.IntegerField(
        null=True, blank=True,
        verbose_name=_(u'first comment')
    )
    last_comment_id = models.IntegerField(
        null=True, blank=True,
        verbose_name=_(u'last comment')
    )
    comments_count = models.IntegerField(
        null=False, blank=False,
        default=0,
        verbose_name=_(u'first comment')
    )
    data = jsonfield.JSONField(default=default_json)
    media = jsonfield.JSONField(default=default_json)

    def __str__(self):
        return (self.title or self.body)[:40]

    def descendant_count(self):
        return (self.rght - self.lft - 1) / 2

    def get_absolute_url(self):
        return urls.reverse('forum_api:thread', kwargs={'pk': self.pk})

    def _rights(self, user_id):
        rights = self.data['rights']
        return rights['all'] | rights['users'].get(str(user_id), 0)

    def read_right(self, user):
        return bool(
            user.is_superuser or (self._rights(user.pk) & ACCESS_READ))

    def write_right(self, user):
        return bool(user.is_superuser or (self._rights(user.pk) & ACCESS_WRITE))

    def moderate_right(self, user):
        return bool(
            user.is_superuser or (self._rights(user.pk) & ACCESS_MODERATE))

    def edit_right(self, user):
        return bool(
            user.is_superuser or (self._rights(user.pk) & ACCESS_EDIT))

    @property
    def moderators(self):
        return User.objects.filter(pk__in=[
            pk for pk, right in self.data['rights']['users'].items()
            if right & ACCESS_MODERATE])

    @property
    def accessed_users(self):
        if self.access_type != THREAD_ACCESS_TYPE_NO_READ:
            return None
        return User.objects.filter(pk__in=[
            pk for pk, right in self.data['rights']['users'].items()
            if right & ACCESS_READ])

    def rights_to_json(self, user):
        return {
            'write': self.write_right(user),
            'moderate': self.moderate_right(user),
            'edit': self.edit_right(user),
            'move': self.edit_right(user),
        }


class Thread(AbstractThread):
    pass


class ThreadCollapseStatus(models.Model):
    """
    Collapsing status saver
    """
    class Meta:
        verbose_name = _('thread access right')
        verbose_name_plural = _('threads access rights')
        unique_together = ('thread', 'user')

    thread = models.ForeignKey(
        Thread, models.PROTECT,
        null=False, blank=False,
        verbose_name=_('thread')
    )
    user = models.ForeignKey(
        User, models.PROTECT,
        null=False, blank=False,
        verbose_name=_('user')
    )
    collapse_threads = models.BooleanField(
        default=False,
        null=False, blank=False,
    )

    collapse_rooms = models.BooleanField(
        default=False,
        null=False, blank=False,
    )
