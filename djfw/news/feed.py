from django.utils.translation import ugettext_lazy as _
from django.contrib.syndication import views
from django.utils import timezone
from django.utils import translation

from . import models


class NewsFeed(views.Feed):
    title = _('Tulius.Com site news')
    link = "/news/"
    description = _('Tulius.Com site news')

    def items(self):
        lang = translation.get_language()
        return models.NewsItem.objects.filter(
            is_published=True,
            published_at__lt=timezone.now(),
            language=lang
        ).order_by('-published_at')

    def item_title(self, item):
        return item.caption

    def item_description(self, item):
        return item.full_text
