"""
Forum engine base Thread entity
"""
import jsonfield
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


class ThreadManager(mptt_models.TreeManager):
    def get_ancestors(self, parent):
        if parent.tree_id:
            return self.filter(
                tree_id=parent.tree_id, lft__lt=parent.lft,
                rght__gt=parent.rght)
        if not parent.parent_id:
            return self.none()
        return self.filter(
            tree_id=parent.parent.tree_id,
            lft__lte=parent.parent.lft, rght__gte=parent.parent.rght)

    def get_descendants(self, parent):
        if parent.get_descendant_count():
            return self.filter(
                tree_id=parent.tree_id, lft__gt=parent.lft,
                rght__lt=parent.rght, deleted=False)
        return self.none()

    def get_protected_descendants(self, parent):
        if parent.get_descendant_count():
            return self.get_descendants(parent).exclude(
                access_type__lt=THREAD_ACCESS_TYPE_NO_READ)
        return self.none()


def default_json():
    return {}


class BaseThread(mptt_models.MPTTModel):
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

    def check_deleted(self):
        if self.deleted:
            return True
        if self.parent:
            return self.parent.check_deleted()
        return False

    def free_access_type(self):
        return self.access_type < THREAD_ACCESS_TYPE_NO_READ

    def is_thread(self):
        return not self.room

    def descendant_count(self):
        return (self.rght - self.lft - 1) / 2


class Thread(BaseThread):
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


class BaseThreadDeleteMark(models.Model):
    class Meta:
        verbose_name = _(u'thread delete mark')
        verbose_name_plural = _(u'threads delete marks')
        abstract = True

    thread = models.ForeignKey(
        'Thread', models.PROTECT,
        blank=False, null=False,
        verbose_name=_(u'thread'),
        related_name='delete_marks',
    )
    user = models.ForeignKey(
        User, models.PROTECT,
        blank=False, null=False,
        verbose_name=_(u'user'),
        related_name='%(app_label)s_delete_marks',
    )
    description = models.TextField(
        verbose_name=_(u'description'),
        blank=True, null=True,
    )

    deleted = models.BooleanField(
        default=True,
        verbose_name=_(u'deleted')
    )

    delete_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('deleted at'),
    )

    def __str__(self):
        return _("%(post)s deleted by %(user)s at %(time)s") % \
               {'post': str(self.thread), 'user': str(self.user),
                'time': self.delete_time}


class ThreadDeleteMark(BaseThreadDeleteMark):
    pass