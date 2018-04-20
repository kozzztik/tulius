from django.db import models
from django.utils.translation import ugettext_lazy as _


class ProfilerMessage(models.Model):
    """
    Profiler message
    """
    class Meta:
        verbose_name = _('profiler report')
        verbose_name_plural = _('profiler reports')
        ordering = ['module_name', 'func_name', '-id']
    
    module_name = models.CharField(
        max_length=255, 
        default='',
        blank=True,
        null=True,
        verbose_name=_('module name'),
        db_index=True,
    )
    
    func_name = models.CharField(
        max_length=255, 
        default='',
        blank=True,
        null=True,
        verbose_name=_('function name'),
        db_index=True,
    )
    
    create_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('create time'),
        db_index=True,
    )
    
    user_id = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name=_('user')
    )
    
    exec_time = models.BigIntegerField(
        blank=False,
        null=False,
        verbose_name=_(u'execution time'),
    )
    
    db_time = models.BigIntegerField(
        blank=False,
        null=False,
        verbose_name=_(u'db work time'),
    )
    
    db_count = models.BigIntegerField(
        blank=False,
        null=False,
        verbose_name=_(u'db requests count'),
    )
    
    template_time = models.BigIntegerField(
        blank=False,
        null=False,
        verbose_name=_(u'template render time'),
    )
    
    template_db_time = models.BigIntegerField(
        blank=False,
        null=False,
        verbose_name=_(u'template db work time'),
    )
    
    template_db_count = models.BigIntegerField(
        blank=False,
        null=False,
        verbose_name=_(u'template db requests count'),
    )
    
    exec_param = models.BigIntegerField(
        blank=True,
        null=True,
        verbose_name=_(u'execution parameter'),
    )
    
    ip = models.GenericIPAddressField(
        verbose_name=_('IP'),
    )
    
    browser = models.CharField(
        max_length=30, 
        default='',
        blank=True,
        null=True,
        verbose_name=_('browser'),
    )
    
    browser_version = models.CharField(
        max_length=10, 
        default='',
        blank=True,
        null=True,
        verbose_name=_('browser version'),
    )
    
    os = models.CharField(
        max_length=30, 
        default='',
        blank=True,
        null=True,
        verbose_name=_('OS'),
    )
    
    os_version = models.CharField(
        max_length=10, 
        default='',
        blank=True,
        null=True,
        verbose_name=_('OS version'),
    )
    
    device = models.CharField(
        max_length=30, 
        default='',
        blank=True,
        null=True,
        verbose_name=_('device'),
    )
    
    mobile = models.BooleanField(
        default=False,
        blank=False,
        null=False,
        verbose_name=_('is mobile'),
    )
    
    error = models.BooleanField(
        default=False,
        blank=False,
        null=False,
        verbose_name=_('error'),
    )
    
    thread_id = models.BigIntegerField(
        blank=True,
        null=True,
        verbose_name=_(u'thread ID'),
    )


class TimeCollapse(models.Model):
    day = models.DateField(
        auto_now_add=False,
        verbose_name=_('day'),
        db_index=True,
    )
    create_time = models.DateTimeField(
        auto_now_add=False,
        verbose_name=_('create time'),
        db_index=True,
    )
    calls_count = models.BigIntegerField(
        blank=False,
        null=False,
        verbose_name=_(u'calls count'),
    )

    anon_calls_count = models.BigIntegerField(
        blank=False,
        null=False,
        verbose_name=_(u'Anonymous calls count'),
    )

    mobiles_count = models.BigIntegerField(
        blank=False,
        null=False,
        verbose_name=_(u'calls count'),
    )
    
    exceptions_count = models.BigIntegerField(
        blank=False,
        null=False,
        verbose_name=_(u'exceptions count'),
    )

    exec_time = models.BigIntegerField(
        blank=False,
        null=False,
        verbose_name=_(u'execution time'),
    )
    
    db_time = models.BigIntegerField(
        blank=False,
        null=False,
        verbose_name=_(u'db work time'),
    )
    
    db_count = models.BigIntegerField(
        blank=False,
        null=False,
        verbose_name=_(u'db requests count'),
    )
    
    template_time = models.BigIntegerField(
        blank=False,
        null=False,
        verbose_name=_(u'template render time'),
    )
    
    template_db_time = models.BigIntegerField(
        blank=False,
        null=False,
        verbose_name=_(u'template db work time'),
    )
    
    template_db_count = models.BigIntegerField(
        blank=False,
        null=False,
        verbose_name=_(u'template db requests count'),
    )


class ClientCollapse(models.Model):
    day = models.DateField(
        auto_now_add=False,
        verbose_name=_('day'),
        db_index=True,
    )
    
    oses = models.TextField(
        verbose_name=_('oses'),
    )
    browsers = models.TextField(
        verbose_name=_('browsers'),
    )
    
    devices = models.TextField(
        verbose_name=_('devices'),
    )
    modules = models.TextField(
        verbose_name=_('devices'),
    )
