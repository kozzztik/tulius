# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django.contrib.syndication.views import Feed
from django.utils.timezone import now
from django.utils import translation
from .models import NewsItem

class NewsFeed(Feed):
    title = _('Tulius.Com site news')
    link = "/news/"
    description = _('Tulius.Com site news')

    def items(self):
        lang = translation.get_language()
        return NewsItem.objects.filter(is_published=True, published_at__lt=now(), language=lang).order_by('-published_at')

    def item_title(self, item):
        return item.caption

    def item_description(self, item):
        return item.full_text