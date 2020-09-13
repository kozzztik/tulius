from django.conf import urls
from django.views.generic import RedirectView

from .feed import NewsFeed
from .views import NewsList, NewsDetail


app_name = 'djfw.news'

urlpatterns = [
    urls.re_path(r'^$', RedirectView.as_view(url='/news/list'), name='index'),
    urls.re_path(r'list$', NewsList.as_view(), name='list'),
    urls.re_path(r'(?P<pk>\d+)/$', NewsDetail.as_view(), name='detail'),
    urls.re_path(r'^feed/$', NewsFeed(), name='feed'),
]
