"""
Forum engine models for Tulius project
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _


User = get_user_model()


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


def default_media():
    return {}
