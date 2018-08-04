from django.conf.urls import url

# TODO: fix this when module moved
from tulius.forum.plugins import ForumPlugin
from .views import SearchView, ExtendedSearchView
from .forms import SearchForm


class GameSearchPlugin(ForumPlugin):
    def search_url(self, thread):
        return self.reverse('search', thread.variation.id)

    def extended_search_url(self, thread):
        return self.reverse('extended_search', thread.variation.id)

    def init_core(self):
        self.core['search_form'] = SearchForm()
        self.urlizer['Thread_search_url'] = self.search_url
        self.urlizer['Thread_extended_search_url'] = self.extended_search_url
        self.templates['search_post'] = 'gameforum/snippets/searched_post.haml'
        self.templates['search'] = 'gameforum/search.haml'
        self.templates['search_form'] = 'gameforum/search_form.haml'

    def get_urls(self):
        return [
            url(
                r'^search/(?P<pk>\d+)/$',
                SearchView.as_view(plugin=self),
                name='search'),
            url(
                r'^extended_search/(?P<pk>\d+)/$',
                ExtendedSearchView.as_view(plugin=self),
                name='extended_search'),
        ]
