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

NO_ACCESS = 0
ACCESS_READ = 1
ACCESS_WRITE = 2
ACCESS_MODERATE = 4
ACCESS_EDIT = 8
ACCESS_NO_INHERIT = 16

ACCESS_OWN = ACCESS_READ + ACCESS_WRITE + ACCESS_EDIT
ACCESS_OPEN = ACCESS_READ + ACCESS_WRITE
ACCESS_MODERATOR = ACCESS_READ + ACCESS_WRITE + ACCESS_MODERATE

DEFAULT_RIGHTS_CHOICES = (
    (None, _(u'access not set')),
    (ACCESS_READ + ACCESS_WRITE, _(u'free access')),
    (ACCESS_READ, _(u'read only access')),
    (ACCESS_READ + ACCESS_NO_INHERIT, _(u'read only access(no inherit)')),
    (NO_ACCESS, _(u'private(no access)')),
)


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
    default_rights = models.SmallIntegerField(
        default=None, blank=True, null=True,
        verbose_name=_(u'access type'),
        choices=DEFAULT_RIGHTS_CHOICES,
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
    data = jsonfield.JSONField(default=default_json)
    media = jsonfield.JSONField(default=default_json)

    def __str__(self):
        return (self.title or self.body)[:40]

    def descendant_count(self):
        return (self.rght - self.lft - 1) / 2

    def get_absolute_url(self):
        return urls.reverse('forum_api:thread', kwargs={'pk': self.pk})

    def rights(self, user_id):
        rights = self.data['rights']
        result = rights['all']
        if user_id:
            result |= rights['users'].get(str(user_id), 0)
        return result

    def read_right(self, user):
        return bool(
            user.is_superuser or (self.rights(user.pk) & ACCESS_READ))

    def write_right(self, user):
        return bool(
            user.is_superuser or (self.rights(user.pk) & ACCESS_WRITE))

    def moderate_right(self, user):
        return bool(
            user.is_superuser or (self.rights(user.pk) & ACCESS_MODERATE))

    def edit_right(self, user):
        return bool(
            user.is_superuser or (self.rights(user.pk) & ACCESS_EDIT))

    @property
    def moderators(self):
        return User.objects.filter(pk__in=[
            pk for pk, right in self.data['rights']['users'].items()
            if right & ACCESS_MODERATE])

    @property
    def accessed_users(self):
        if self.default_rights != NO_ACCESS:
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
