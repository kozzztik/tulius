from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from django.template.defaultfilters import filesizeformat


class Smile(models.Model):
    class Meta:
        verbose_name = _('smile')
        verbose_name_plural = _('smiles')

    name = models.CharField(
        max_length=500,
        unique=False,
        verbose_name=_('name')
    )

    text = models.CharField(
        max_length=500,
        unique=False,
        verbose_name=_('text')
    )

    image = models.ImageField(
        upload_to='wysibb/smiles/',
        verbose_name=_('image'),
    )

    def preview_image(self):
        if not self.image:
            return None
        return '<img src="' + str(self.image.url) + '"/>'

    def __str__(self):
        return str(self.name)

    preview_image.allow_tags = True
    preview_image.short_description = _('image')


class UploadedFile(models.Model):
    class Meta:
        verbose_name = _('uploaded file')
        verbose_name_plural = _('uploaded files')
        ordering = ('-id', )

    filename = models.CharField(
        max_length=500,
        unique=False,
        verbose_name=_('filename')
    )

    body = models.FileField(
        upload_to='wysibb/uploaded_files/',
        verbose_name=_('body'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        models.PROTECT,
        null=True,
        blank=True,
        related_name='wysibb_files',
        verbose_name=_('user')
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('create time'),
    )

    mime = models.CharField(
        max_length=500,
        unique=False,
        verbose_name=_('mime type')
    )

    file_size = models.IntegerField(
        default=0,
        verbose_name=_(u'file length'),
    )

    def __unicode__(self):
        return self.filename

    def get_absolute_url(self):
        return self.body.url if self.body else None

    def file_size_formated(self):
        return filesizeformat(self.file_size)

    def filename_link(self):
        if not self.body:
            return self.filename
        return '<a href="%s">%s</a>' % (self.body.url, self.filename)

    get_absolute_url.short_description = _('URL')
    file_size_formated.short_description = _('file size')
    filename_link.allow_tags = True
    filename_link.short_description = _('File')


class UploadedImage(models.Model):
    """
    Uploaded images
    """
    class Meta:
        verbose_name = _('uploaded image')
        verbose_name_plural = _('uploaded images')
        ordering = ('-id', )

    filename = models.CharField(
        max_length=500,
        unique=False,
        verbose_name=_('filename')
    )

    image = models.ImageField(
        upload_to='wysibb/uploaded_image/',
        verbose_name=_('image'),
    )

    thumb = models.ImageField(
        upload_to='wysibb/uploaded_thumbs/',
        verbose_name=_('thumbnail'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        models.PROTECT,
        null=True,
        blank=True,
        related_name='wysibb_images',
        verbose_name=_('user')
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('create time'),
    )

    mime = models.CharField(
        max_length=500,
        unique=False,
        verbose_name=_('mime type')
    )

    file_size = models.IntegerField(
        default=0,
        verbose_name=_(u'file length'),
    )

    def __unicode__(self):
        return self.filename

    def preview_image(self):
        if (not self.image) or (not self.thumb):
            return ""
        return '<a href="%s"><img src="%s" style="max-height: ' \
            '85px; max-width: 85px"/></a>' % (
                self.image.url, self.thumb.url)

    def get_absolute_url(self):
        return self.body.url if self.body else None

    def file_size_formated(self):
        return filesizeformat(self.file_size)

    get_absolute_url.short_description = _('URL')
    preview_image.short_description = _('image')
    file_size_formated.short_description = _('file size')
    preview_image.allow_tags = True
