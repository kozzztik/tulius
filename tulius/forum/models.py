"""
Forum engine models for Tulius project
"""
import jsonfield
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey, TreeManager


User = get_user_model()
COMMENTS_ON_PAGE = 25


class UploadedFile(models.Model):
    """
    Uploaded Files
    """
    class Meta:
        verbose_name = _('uploaded file')
        verbose_name_plural = _('uploaded files')

    user = models.ForeignKey(
        User, models.PROTECT,
        null=False,
        blank=False,
        related_name='forum_files',
        verbose_name=_('user')
    )
    name = models.CharField(
        max_length=500,
        unique=False,
        verbose_name=_('name')
    )
    mime = models.CharField(
        max_length=500,
        unique=False,
        verbose_name=_('mime type')
    )
    body = models.FileField(
        upload_to='forum_uploads',
        verbose_name=_('file')
    )
    file_length = models.IntegerField(
        default=0,
        verbose_name=_(u'file length'),
    )
    create_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('uploaded at'),
    )

    def is_image(self):
        return self.mime[0:5] == 'image'

    def __unicode__(self):
        """
        Provides unicode string post representation
        """
        return self.name


THREAD_ACCESS_TYPE_NOT_SET = 0
THREAD_ACCESS_TYPE_OPEN = 1
THREAD_ACCESS_TYPE_NO_WRITE = 2
THREAD_ACCESS_TYPE_NO_READ = 3
THREAD_ACCESS_READ = 1
THREAD_ACCESS_WRITE = 2
THREAD_ACCESS_MODERATE = 4
THREAD_ACCESS_MODERATOR = THREAD_ACCESS_READ + THREAD_ACCESS_WRITE + \
                          THREAD_ACCESS_MODERATE

THREAD_ACCESS_TYPE_CHOICES = (
    (THREAD_ACCESS_TYPE_NOT_SET, _(u'access not set')),
    (THREAD_ACCESS_TYPE_OPEN, _(u'free access')),
    (THREAD_ACCESS_TYPE_NO_WRITE, _(u'read only access')),
    (THREAD_ACCESS_TYPE_NO_READ, _(u'private(no access)')),
)

THREAD_ACCESS_CHOICES = (
    (
        THREAD_ACCESS_READ + THREAD_ACCESS_WRITE,
        _(u'read and write rights')),
    (
        THREAD_ACCESS_READ,
        _(u'read right')),
    (
        THREAD_ACCESS_READ + THREAD_ACCESS_WRITE + THREAD_ACCESS_MODERATE,
        _(u'read, write and moderate')),
    (
        THREAD_ACCESS_WRITE,
        _(u'write only right')),
    (
        THREAD_ACCESS_READ + THREAD_ACCESS_MODERATE,
        _(u'read and moderate right(no write)')),
)


class SitedModelMixin(models.Model):
    class Meta:
        abstract = True
    plugin_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('plugin')
    )


class ThreadManager(TreeManager):
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


def default_media():
    return {}


class Thread(MPTTModel, SitedModelMixin):
    """
    Forum thread
    """
    class Meta:
        verbose_name = _('thread')
        verbose_name_plural = _('threads')
        ordering = ['-important', 'id']

    objects = ThreadManager()

    title = models.CharField(
        max_length=255,
        unique=False,
        verbose_name=_('title')
    )
    body = models.TextField(verbose_name=_('body'))
    parent = TreeForeignKey(
        'self', models.PROTECT,
        null=True,
        blank=True,
        related_name='children',
        verbose_name=_('parent thread')
    )
    room = models.BooleanField(
        default=False,
        verbose_name=_(u'room')
    )
    user = models.ForeignKey(
        User, models.PROTECT,
        related_name='forum_threads',
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
        null=True,
        blank=True,
        verbose_name=_(u'first comment')
    )
    last_comment_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name=_(u'last comment')
    )
    comments_count = models.IntegerField(
        null=False,
        blank=False,
        default=0,
        verbose_name=_(u'first comment')
    )
    data1 = models.IntegerField(
        null=True,
        blank=True,
        verbose_name=_(u'public comments'),
    )
    data2 = models.IntegerField(
        null=True,
        blank=True,
        verbose_name=_(u'protected comments'),
    )
    media = jsonfield.JSONField(default=default_media)

    def __str__(self):
        return self.title[:40] if self.title else self.body[:40]

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

    def room_comments_count(self):
        comments = Thread.objects.get_descendants(self).filter(
            room=False, deleted=False
        ).aggregate(
            comments_sum=models.Sum('comments_count'))
        return comments['comments_sum']


class ThreadAccessRight(models.Model):
    """
    Right to access forum thread
    """
    class Meta:
        verbose_name = _('thread access right')
        verbose_name_plural = _('threads access rights')
        unique_together = ('thread', 'user')

    thread = models.ForeignKey(
        Thread, models.PROTECT,
        null=False,
        blank=False,
        related_name='granted_rights',
        verbose_name=_('thread')
    )
    user = models.ForeignKey(
        User, models.PROTECT,
        null=False,
        blank=False,
        related_name='forum_theads_rights',
        verbose_name=_('user')
    )
    access_level = models.SmallIntegerField(
        default=THREAD_ACCESS_READ + THREAD_ACCESS_WRITE,
        verbose_name=_(u'access rights'),
        choices=THREAD_ACCESS_CHOICES,
    )


class ThreadCollapseStatus(models.Model):
    """
    Collapsing status rememberer
    """
    class Meta:
        verbose_name = _('thread access right')
        verbose_name_plural = _('threads access rights')
        unique_together = ('thread', 'user')

    thread = models.ForeignKey(
        Thread, models.PROTECT,
        null=False,
        blank=False,
        verbose_name=_('thread')
    )
    user = models.ForeignKey(
        User, models.PROTECT,
        null=False,
        blank=False,
        verbose_name=_('user')
    )
    collapse_threads = models.BooleanField(
        default=False,
        null=False,
        blank=False,
    )

    collapse_rooms = models.BooleanField(
        default=False,
        null=False,
        blank=False,
    )


class Comment(SitedModelMixin):
    """
    Forum comment
    """
    class Meta:
        verbose_name = _('comment')
        verbose_name_plural = _('comments')
        ordering = ['id']

    title = models.CharField(
        max_length=255,
        unique=False,
        verbose_name=_('title')
    )

    body = models.TextField(
        verbose_name=_('body')
    )

    parent = TreeForeignKey(
        Thread, models.PROTECT,
        null=False,
        blank=False,
        related_name='comments',
        verbose_name=_('thread')
    )
    user = models.ForeignKey(
        User, models.PROTECT,
        null=False,
        blank=False,
        related_name='forum_comments',
        verbose_name=_('author')
    )
    editor = models.ForeignKey(
        User, models.PROTECT,
        null=True,
        blank=True,
        related_name='forum_comments_edited',
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
    data1 = models.IntegerField(
        null=True,
        blank=True,
    )
    data2 = models.IntegerField(
        null=True,
        blank=True,
    )
    media = jsonfield.JSONField(default=default_media)

    def __str__(self):
        return self.title[:40] if self.title else self.body[:40]

    def is_thread(self):
        return self.id == self.parent.first_comment_id


class ThreadReadMark(models.Model):
    """
    Mark on thread, what last post was readed
    """
    class Meta:
        verbose_name = _('thread read mark')
        verbose_name_plural = _('thread read marks')

    thread = models.ForeignKey(
        Thread, models.PROTECT,
        null=False,
        blank=False,
        related_name='read_marks',
        verbose_name=_('thread'),
    )
    user = models.ForeignKey(
        User, models.PROTECT,
        null=False,
        blank=False,
        related_name='forum_readed_threads',
        verbose_name=_('user'),
    )
    readed_comment = models.ForeignKey(
        Comment, models.PROTECT,
        null=False,
        blank=False,
        related_name='readed_users',
        verbose_name=_('readed comment'),
    )
    not_readed_comment = models.ForeignKey(
        Comment, models.PROTECT,
        null=True,
        blank=True,
        related_name='not_readed_users',
        verbose_name=_('not readed comment'),
    )


class CommentLike(models.Model):
    class Meta:
        verbose_name = _('comment like')
        verbose_name_plural = _('comments likes')

    user = models.ForeignKey(
        User, models.PROTECT,
        null=False,
        blank=False,
        related_name='liked_comments',
        verbose_name=_('user'),
    )
    comment = models.ForeignKey(
        Comment, models.PROTECT,
        null=False,
        blank=False,
        related_name='liked',
        verbose_name=_('comment'),
    )


class ThreadDeleteMark(models.Model):
    class Meta:
        verbose_name = _(u'thread delete mark')
        verbose_name_plural = _(u'threads delete marks')

    thread = models.ForeignKey(
        Thread, models.PROTECT,
        blank=False,
        null=False,
        verbose_name=_(u'thread'),
        related_name='delete_marks',
    )
    user = models.ForeignKey(
        User, models.PROTECT,
        blank=False,
        null=False,
        verbose_name=_(u'user'),
        related_name='thread_delete_marks',
    )
    description = models.TextField(
        verbose_name=_(u'description'),
        blank=True,
        null=True,
    )

    deleted = models.BooleanField(
        default=True,
        verbose_name=_(u'deleted')
    )

    delete_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('deleted at'),
    )

    def __unicode__(self):
        return _("%(post)s deleted by %(user)s at %(time)s") % \
               {'post': str(self.thread), 'user': str(self.user),
                'time': self.delete_time}


class CommentDeleteMark(models.Model):
    class Meta:
        verbose_name = _(u'comment delete mark')
        verbose_name_plural = _(u'comments delete marks')

    comment = models.ForeignKey(
        Comment, models.PROTECT,
        blank=False,
        null=False,
        verbose_name=_(u'comment'),
        related_name='delete_marks',
    )
    user = models.ForeignKey(
        User, models.PROTECT,
        blank=False,
        null=False,
        verbose_name=_(u'user'),
        related_name='comments_delete_marks',
    )
    description = models.TextField(
        verbose_name=_(u'description'),
        blank=True,
        null=True,
    )
    deleted = models.BooleanField(
        default=True,
        verbose_name=_(u'deleted')
    )
    delete_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('deleted at'),
    )

    def __unicode__(self):
        return _("%(post)s deleted by %(user)s at %(time)s") % {
            'post': str(self.comment), 'user': str(self.user),
            'time': self.delete_time}


class OnlineUser(models.Model):
    class Meta:
        verbose_name = _(u'online user')
        verbose_name_plural = _(u'online users')
        unique_together = ['user', 'thread']

    user = models.ForeignKey(
        User, models.PROTECT,
        blank=False,
        null=False,
        verbose_name=_(u'user'),
        related_name='forum_visit',
    )
    visit_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('visit time'),
    )
    thread = models.ForeignKey(
        Thread, models.PROTECT,
        blank=False,
        null=False,
        verbose_name=_(u'thread'),
        related_name='visit_marks',
    )

    def __str__(self):
        return str(self.user)


class VotingVote(models.Model):
    """
    Voting choice
    """
    class Meta:
        verbose_name = _('voting vote')
        verbose_name_plural = _('voting votes')
        unique_together = ('user', 'comment')

    choice = models.IntegerField(
        blank=False,
        null=False,
        verbose_name=_('choice')
    )
    user = models.ForeignKey(
        User, models.PROTECT,
        null=False,
        blank=False,
        verbose_name=_(u'user'),
        related_name='voting_votes',
    )
    comment = models.ForeignKey(
        Comment, models.PROTECT,
        null=False,
        blank=False,
        related_name='votes',
        verbose_name=_(u'comment'),
    )

    def __str__(self):
        return f'{self.comment.title} - {self.choice}({self.user})'
