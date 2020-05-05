import os

from django.db import models
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext_lazy as _


class BackupCategory(models.Model):
    """
    BackupCategory
    """
    class Meta:
        verbose_name = _('backup category')
        verbose_name_plural = _('backup categories')

    name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('name')
    )
    verbose_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('verbose name')
    )
    saved_backups = models.PositiveIntegerField(
        blank=False,
        null=False,
        default=0,
        verbose_name=_(u'saved backups'),
    )
    enabled = models.BooleanField(
        blank=False,
        null=False,
        default=True,
        verbose_name=_(u'enabled'),
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('description')
    )

    def clear_backups(self):
        backups = Backup.objects.filter(category=self).order_by('-id')
        if self.saved_backups and (self.saved_backups < backups.count()):
            backups = backups[self.saved_backups:backups.count()]
            obj_count = backups.count()
            ids = [backup.id for backup in backups]
            backups = Backup.objects.filter(id__in=ids)
            for backup in backups:
                backup.delete()
            return obj_count
        return 0

    def __unicode__(self):
        return self.verbose_name


class Backup(models.Model):
    """
    Backup
    """
    class Meta:
        verbose_name = _('backup')
        verbose_name_plural = _('backups')

    category = models.ForeignKey(
        BackupCategory, models.PROTECT,
        null=False,
        blank=False,
        related_name='backups',
        verbose_name=_('category')
    )
    create_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('create time'),
    )
    size = models.PositiveIntegerField(
        blank=False,
        null=False,
        default=0,
        verbose_name=_(u'size'),
    )

    def __str__(self):
        return "%s %s" % (self.category.name, self.create_time)

    def backups_dir(self):
        dir_path = getattr(settings, 'INSTALLER_BACKUPS_DIR', None)
        if not dir_path:
            raise ImproperlyConfigured('Backups directory not set.')
        return dir_path

    def file_name(self):
        return "%s.tar.gz" % self.pk

    def file_size(self):
        from django.template.defaultfilters import filesizeformat
        return filesizeformat(self.size)

    file_size.short_description = _(u'size')

    def path(self):
        return os.path.join(self.backups_dir(), self.file_name())

    @models.permalink
    def get_absolute_url(self):
        return 'installer:backup', (), {'object_id': self.id}

    def url(self):
        return '<a href="%s">%s</a>' % (
            self.get_absolute_url(), self.get_absolute_url())

    url.short_description = _(u'URL')
    url.allow_tags = True

    def delete(self, using=None, keep_parents=False):
        if os.path.exists(self.path()):
            os.remove(self.path())
        super(Backup, self).delete(using=using, keep_parents=keep_parents)


def get_lock_file_name():
    lock_file_name = getattr(settings, 'INSTALLER_LOCK_FILE', None)
    if not lock_file_name:
        lock_file_name = settings.BASE_DIR + 'maintaince.lock'
    return lock_file_name


class Revision(models.Model):
    class Meta:
        verbose_name = _('Revision')
        verbose_name_plural = _('Revisions')

    number = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('revision')
    )
    author = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('revision')
    )
    comment = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('revision')
    )
    time = models.DateTimeField(
        auto_now_add=False,
        verbose_name=_('end time'),
    )

    def __str__(self):
        return "%s %s %s" % (self.number, self.author, self.comment)


class MaintenanceLog(models.Model):
    """
    UpdateLog
    """
    class Meta:
        verbose_name = _('Maintenance')
        verbose_name_plural = _('Maintenance')

    STATE_IN_PROGRESS = 0
    STATE_SUCCESS = 1
    STATE_ERROR = 2
    STATE_CHOICES = (
        (STATE_IN_PROGRESS, _('In progress')),
        (STATE_SUCCESS, _('Success')),
        (STATE_ERROR, _('Error')),
    )

    revision = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('revision')
    )
    start_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('start time'),
    )
    end_time = models.DateTimeField(
        auto_now_add=False,
        null=True,
        blank=True,
        verbose_name=_('end time'),
    )
    status = models.CharField(
        max_length=255,
        blank=True,
        null=False,
        default='',
        verbose_name=_('status')
    )
    state = models.SmallIntegerField(
        choices=STATE_CHOICES,
        blank=False,
        null=False,
        default=STATE_IN_PROGRESS,
        verbose_name=_('state')
    )
    waiting_user = models.BooleanField(
        blank=False,
        null=False,
        default=False,
        verbose_name=_('waiting user')
    )
    buildout_update_time = models.BigIntegerField(
        editable=False,
        null=True,
        blank=True,
    )
    comment = models.CharField(
        max_length=255,
        blank=True,
        null=False,
        default='',
        verbose_name=_('comment')
    )

    operations = models.TextField(
        max_length=255,
        blank=True,
        null=False,
        default='',
        verbose_name=_('operations')
    )

    operation = models.TextField(
        max_length=255,
        blank=True,
        null=False,
        default='',
        verbose_name=_('operation')
    )

    params = models.TextField(
        max_length=255,
        blank=True,
        null=False,
        default='',
        verbose_name=_('Parameters')
    )

    def __str__(self):
        return "%s" % (self.start_time,)

    def save(
            self, force_insert=False, force_update=False, using=None,
            update_fields=None):
        file_name = get_lock_file_name()
        was_none = not self.pk
        if (not was_none) and self.end_time and (os.path.exists(file_name)):
            f = open(file_name, 'r')
            old_id = None
            try:
                old_id = int(f.read())
            finally:
                f.close()
            if old_id == self.id:
                os.remove(file_name)
        super(MaintenanceLog, self).save(
            force_insert=force_insert, force_update=force_update,
            using=using, update_fields=update_fields)
        if was_none and not self.end_time:
            if os.path.exists(file_name):
                os.remove(file_name)
            f = open(file_name, 'w')
            f.write(str(self.id))
            f.close()


class MaintenanceLogMessage(models.Model):
    """
    UpdateLog
    """
    class Meta:
        verbose_name = _('Maintenance log message')
        verbose_name_plural = _('Maintenance log messages')

    mainteince = models.ForeignKey(
        MaintenanceLog, models.PROTECT,
        null=False,
        blank=False,
        related_name='messages',
    )

    start_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('start time'),
    )

    text = models.TextField(
        default='',
        verbose_name=_('text')
    )


class MaintainceChangelist(models.Model):
    mainteince = models.ForeignKey(
        MaintenanceLog, models.PROTECT,
        null=False,
        blank=False,
    )
    revision = models.ForeignKey(
        Revision, models.PROTECT,
        null=False,
        blank=False,
    )
