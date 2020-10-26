import os

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import filesizeformat


class PhotoAlbum(models.Model):
    class Meta:
        verbose_name = _('photo album')
        verbose_name_plural = _('photo albums')

    title = models.CharField(
        verbose_name=_('title'),
        max_length=100
    )

    description = models.TextField(
        verbose_name='description',
        blank=True,
    )

    enabled = models.BooleanField(
        blank=False,
        null=False,
        default=False,
        verbose_name=_(u'enabled'),
    )

    title_photo = models.ForeignKey(
        'Photo',
        models.PROTECT,
        null=True,
        blank=True,
        verbose_name=_('title photo'),
    )

    def preview_image_url(self):
        if not self.title_photo:
            return None
        if not self.title_photo.thumbnail:
            return None
        image_path = os.path.join(
            settings.MEDIA_URL, self.title_photo.thumbnail.url)
        return '<img src="' + str(image_path) +\
               '" style="max-height: 100px; max-width: 100px"/>'

    def photo_count(self):
        return self.photos.all().count()

    def tags(self):
        return '[photoalbum=%s]' % self.id

    def __unicode__(self):
        return self.title

    preview_image_url.short_description = _('image')
    photo_count.short_description = _('photo count')
    tags.short_description = _('Tag')
    preview_image_url.allow_tags = True


class Photo(models.Model):
    class Meta:
        verbose_name = _('photo')
        verbose_name_plural = _('photos')

    album = models.ForeignKey(
        PhotoAlbum,
        models.PROTECT,
        null=False,
        blank=False,
        related_name='photos',
        verbose_name=_('album')
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        models.PROTECT,
        null=True,
        blank=True,
        related_name='photos',
        verbose_name=_('user')
    )

    title = models.CharField(
        verbose_name=_('title'),
        max_length=100
    )

    description = models.TextField(
        verbose_name='description',
        blank=True,
    )

    image = models.ImageField(
        upload_to='photos/',
        verbose_name=_('image'),
    )

    thumbnail = models.ImageField(
        upload_to='photos/thumb/',
        verbose_name=_('thumbnail'),
    )

    file_length = models.IntegerField(
        default=0,
        verbose_name=_(u'file length'),
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('created at'),
    )

    def __unicode__(self):
        return self.title

    def preview_image_url(self):
        if not self.thumbnail:
            return None
        image_path = os.path.join(settings.MEDIA_URL, self.thumbnail.url)
        return '<img src="' + str(image_path) +\
               '" style="max-height: 100px; max-width: 100px"/>'

    def get_absolute_url(self):
        return self.image.url if self.image else None

    def file_size(self):
        return filesizeformat(self.file_length)

    def short_tag(self):
        return '[photosmall=%s]' % self.id

    def big_tag(self):
        return '[photo=%s]' % self.id

    get_absolute_url.short_description = _('URL')
    preview_image_url.short_description = _('image')
    file_size.short_description = _('file length')
    preview_image_url.allow_tags = True
