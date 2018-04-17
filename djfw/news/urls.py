from django.conf.urls import url
from django.views.generic import RedirectView

from .feed import NewsFeed
from .views import NewsList, NewsDetail


app_name = 'djfw.news'

urlpatterns = [
    url(r'^$', RedirectView.as_view(url='/news/list'), name='index'),
    url(r'list$', NewsList.as_view(), name='list'),
    url(r'(?P<pk>\d+)/$', NewsDetail.as_view(), name='detail'),
    url(r'^feed/$', NewsFeed(), name='feed'),
]
