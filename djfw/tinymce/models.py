import os

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Emotion(models.Model):
    """
    Editor emotion
    """
    class Meta:
        verbose_name = _('emotion')
        verbose_name_plural = _('emotions')
    
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
    
    filename = models.CharField(
        max_length=500, 
        unique=False, 
        verbose_name=_('filename')
    )

    def __unicode__(self):
        return self.name


class FileUpload(models.Model):
    """
    Editor uploaded files
    """
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
        upload_to='tinymce/uploaded_files/',
        verbose_name=_('body'),
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        models.PROTECT,
        null=True,
        blank=True,
        related_name='tinymce_uploads', 
        verbose_name=_('user')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('created at'),
    )
    
    mime = models.CharField(
        max_length=500, 
        unique=False, 
        verbose_name=_('mime type'),
        null=False,
        blank=True,
        default=''
    )

    file_length = models.IntegerField(
        default=0,
        verbose_name=_(u'file length'),
    )
    
    def is_image(self):
        return (self.mime[0:5] == 'image')
    
    def __unicode__(self):
        return self.filename

    def preview_image_url(self):
        if not self.body:
            return None
        if self.is_image():
            image_path = os.path.join(settings.MEDIA_URL, self.body.url)
        else:
            image_path = os.path.join(
                settings.STATIC_URL, 'tinymce/img/box_address.png')
        return f'<img src="{image_path}" style="max-height: 85px; ' \
               f'max-width: 85px"/>'
    
    def get_absolute_url(self):
        return self.body.url if self.body else None
        
    def file_size(self):
        from django.template.defaultfilters import filesizeformat
        return filesizeformat(self.file_length)
    
    get_absolute_url.short_description = _('URL')
    preview_image_url.short_description = _('image')
    file_size.short_description = _('file length')
    preview_image_url.allow_tags = True
