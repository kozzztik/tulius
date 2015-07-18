from django.utils.translation import ugettext_lazy as _
from django.db import models
from djfw.common.models import AbstractBaseModel
from mptt.models import MPTTModel, TreeForeignKey
from django.utils import translation

class TreePage(MPTTModel, AbstractBaseModel):
    parent = TreeForeignKey(
        'self', 
        null=True, 
        blank=True, 
        related_name='children', 
        verbose_name=_('parent page'),
        db_index=True,
    )
    url = models.CharField(
        verbose_name=_('URL'), 
        max_length=100, 
        db_index=True,
    )
    title = models.CharField(
        verbose_name=_('title'), 
        max_length=200
    )
    content = models.TextField(
        blank=True,
        verbose_name=_('content'), 
    )
    is_enabled = models.BooleanField(
        verbose_name=_('is enabled')
    )
    show_on_home = models.BooleanField(
        verbose_name=_('show on home')
    )
    
    meta_title = models.CharField(
        verbose_name=_('META title'), 
        max_length=100,
        default=''
    )
    
    keywords = models.CharField(
        verbose_name=_('keywords'), 
        default='',
        blank=True,
        max_length=200
    )

    meta_description = models.CharField(
        verbose_name=_('META description'), 
        max_length=200,
        default=''
    )
    
    language = models.CharField(
        verbose_name=_('language'), 
        max_length=10, 
        null=False, 
        blank=False,
        editable=False
    )
    class Meta:
        verbose_name = _('tree page')
        verbose_name_plural = _('tree pages')
        ordering = ('tree_id', 'level','position', 'lft',)
    
    def __unicode__(self):
        url = unicode(self.url)
        title = self.title
        import types
        if isinstance(title, types.StringType):
            title = title.decode('utf8')
        str = u"%s -- %s" % (url, title)
        return str

    def get_absolute_url(self):
        return self.url
    
    def tree_unicode(self):
        return ('----' * self.level) + (' ' if self.level else '') + self.__unicode__()
    
    def childs_on_home(self):
        lang = translation.get_language()
        return TreePage.objects.filter(parent=self, show_on_home=True, is_enabled=True, language=lang).order_by('position')
    
    def save(self, *args, **kwargs):
        if not self.language:
            self.language = translation.get_language()
        super(TreePage, self).save(*args, **kwargs)