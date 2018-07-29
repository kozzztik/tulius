from django.utils import translation
from django.views.generic import ListView, DetailView
from . import models


class NewsList(ListView):
    template_name = 'news/newsitem_list.haml'

    def get_queryset(self):
        lang = translation.get_language()
        return models.NewsItem.objects.filter(
            is_published=True, language=lang).order_by('-published_at')


class NewsDetail(DetailView):
    template_name = 'news/newsitem_detail.haml'

    def get_queryset(self):
        lang = translation.get_language()
        return models.NewsItem.objects.filter(
            is_published=True, language=lang).order_by('-published_at')
