from django.utils import translation
from django.views.generic import ListView, DetailView
from .models import NewsItem

class NewsList(ListView):
    template_name='news/newsitem_list.haml'
    def get_queryset(self):
        lang = translation.get_language()
        return NewsItem.objects.filter(is_published=True, language=lang).order_by('-published_at')
        
class NewsDetail(DetailView):
    template_name='news/newsitem_detail.haml'
    def get_queryset(self):
        lang = translation.get_language()
        return NewsItem.objects.filter(is_published=True, language=lang).order_by('-published_at')