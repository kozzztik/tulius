from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
import logging

LOGGING_LEVEL_CHOICES = (
    (logging.NOTSET, _(u'NOT SET')),
    (logging.DEBUG, _(u'DEBUG')),
    (logging.INFO, _(u'INFO')),
    (logging.WARNING, _(u'WARNING')),
    (logging.ERROR, _(u'ERROR')),
    (logging.CRITICAL, _(u'CRITICAL')),
)


class LogMessage(models.Model):
    """
    log message
    """
    class Meta:
        verbose_name = _('log message')
        verbose_name_plural = _('log messages')
        ordering = ['-id', '-create_time']
    
    level = models.SmallIntegerField(
        default=logging.NOTSET,
        verbose_name=_(u'level'),
        choices=LOGGING_LEVEL_CHOICES,
        db_index=True
    )
    
    create_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('create time'),
    )
    
    logger_name = models.CharField(
        max_length=255, 
        default='',
        blank=True,
        null=True,
        verbose_name=_('logger name')
    )
    
    module_name = models.CharField(
        max_length=255, 
        default='',
        blank=True,
        null=True,
        verbose_name=_('module name')
    )
    
    body = models.TextField(
        verbose_name=_('body')
    )
    
    def __unicode__(self):
        return "%s : %s" % (self.get_level_display(),  self.body)
    

class ExceptionMessage(models.Model):
    """
    Exception log message
    """
    class Meta:
        verbose_name = _('exception')
        verbose_name_plural = _('exceptions')
        ordering = ['-id']
        
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        null=True,
        blank=True,
        related_name='exceptions', 
        verbose_name=_('user')
    )
    
    create_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Occur time'),
    )
    
    classname = models.CharField(
        max_length=50, 
        unique=False, 
        verbose_name=_('class name')
    )
    
    title = models.CharField(
        max_length=255, 
        unique=False, 
        verbose_name=_('title')
    )
    
    location = models.CharField(
        max_length=255, 
        unique=False, 
        verbose_name=_('location')
    )
    
    path = models.CharField(
        max_length=255, 
        unique=False, 
        verbose_name=_('path')
    )
    
    get_data = models.CharField(
        max_length=255, 
        unique=False, 
        verbose_name=_('get')
    )
    
    post_data = models.CharField(
        max_length=255, 
        unique=False, 
        verbose_name=_('post')
    )
    
    def __unicode__(self):
        return "%s %s" % (self.classname, self.path)
    
    def user_link(self):
        if self.user_id:
            return '<a href="%s">%s</a>' % (
                self.user.get_absolute_url(), str(self.user), )
        else:
            return ""
    
    def path_link(self):
        return '<a href="%s">%s</a>' % (self.path, self.path,)

    user_link.allow_tags = True
    user_link.short_description = _('user')
    path_link.allow_tags = True
    path_link.short_description = _('path')
    
    @models.permalink
    def get_absolute_url(self):
        return 'admin:logger_exceptionmessage_change', (self.id, ), {}


class ExceptionCookie(models.Model):
    """
    Exception cookie
    """
    
    class Meta:
        verbose_name = _('exception cookie')
        verbose_name_plural = _('exception cookies')
        ordering = ["name"]
        
    exception_message = models.ForeignKey(
        ExceptionMessage, 
        related_name='cookies', 
        verbose_name=_('exception')
    )
    
    name = models.CharField(
        max_length=50, 
        unique=False, 
        verbose_name=_('name')
    )
    
    value = models.CharField(
        max_length=255, 
        unique=False, 
        verbose_name=_('value')
    )
    
    def __unicode__(self):
        return "%s = %s" % (self.name, self.value)
    

class ExceptionMETAValue(models.Model):
    """
    Exception META value
    """
    
    class Meta:
        verbose_name = _('exception META value')
        verbose_name_plural = _('exception META values')
        ordering = ["name"]
        
    exception_message = models.ForeignKey(
        ExceptionMessage, 
        related_name='metas', 
        verbose_name=_('exception')
    )
    
    name = models.CharField(
        max_length=50, 
        unique=False, 
        verbose_name=_('name')
    )
    
    value = models.CharField(
        max_length=255, 
        unique=False, 
        verbose_name=_('value')
    )
    
    def __unicode__(self):
        return "%s = %s" % (self.name, self.value)


class ExceptionTraceback(models.Model):
    """
    Exception traceback record
    """
    
    class Meta:
        verbose_name = _('exception traceback record')
        verbose_name_plural = _('exception traceback records')
        
    exception_message = models.ForeignKey(
        ExceptionMessage, 
        related_name='traceback', 
        verbose_name=_('exception')
    )
    
    filename = models.CharField(
        max_length=250, 
        unique=False, 
        verbose_name=_('file name')
    )
    
    line_num = models.IntegerField(
        default=0,
        verbose_name=_(u'Line number'),
    )
    
    function_name = models.CharField(
        max_length=100, 
        unique=False, 
        verbose_name=_('function name')
    )
    
    body = models.CharField(
        max_length=250, 
        unique=False, 
        verbose_name=_('text')
    )
    
    def __unicode__(self):
        return "%s %s %s" % (self.filename, self.line_num, self.function_name)
