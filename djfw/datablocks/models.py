from django.utils.translation import gettext_lazy as _
from django.utils import translation
from django.db import models
from django.core.cache import cache

CACHE_PREFIX = 'datablocks_ids_'


class DataBlockManager(models.Manager):
    def languaged_ids(self):
        lang = translation.get_language()
        value = cache.get(CACHE_PREFIX + lang)
        if value is not None:
            return value
        full_list = self.all()
        filtered_list = []
        for block in full_list:
            found = False
            for subblock in filtered_list:
                if subblock[0] == block.name and \
                        subblock[1] == block.urls and \
                        subblock[2] == block.exclude_urls:
                    if (block.language == lang) or (block.language is None):
                        subblock[3] = block.language
                        subblock[4] = block.id
                    found = True
                    break
            if not found:
                filtered_list += [
                    [block.name, block.urls, block.exclude_urls,
                     block.language, block.id]]
        value = [data[4] for data in filtered_list]
        cache.set(CACHE_PREFIX + lang, value)
        return value

    def languaged(self):
        return self.filter(pk__in=self.languaged_ids())


class DataBlock(models.Model):
    class Meta:
        verbose_name = _(u'data block')
        verbose_name_plural = _(u'data blocks')
        ordering = ['name']

    objects = DataBlockManager()

    name = models.CharField(
        max_length=100,
        blank=False,
        null=False,
        verbose_name=_(u'name')
    )
    full_text = models.TextField(
        default='',
        blank=True,
        null=True,
        verbose_name=_(u'text')
    )

    urls = models.TextField(
        default='',
        blank=True,
        null=True,
        verbose_name=_(u'URLs')
    )

    exclude_urls = models.TextField(
        default='',
        blank=True,
        null=True,
        verbose_name=_(u'exclude URLs')
    )
    language = models.CharField(
        verbose_name=_('language'),
        max_length=10,
        null=True,
        blank=True,
        editable=False
    )

    def __str__(self):
        return str(self.name)

    def save(
            self, force_insert=False, force_update=False, using=None,
            update_fields=None):
        lang = translation.get_language()
        drop_cache = False
        if lang != self.language:
            self.language = lang
            self.pk = None
            drop_cache = True
        super().save(
            force_insert=force_insert, force_update=force_update,
            using=using, update_fields=update_fields)
        if drop_cache:
            cache.delete(CACHE_PREFIX + lang)
