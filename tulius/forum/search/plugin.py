from django import urls
from django.conf.urls import url

# TODO: fix this when module moved
from tulius.forum.plugins import ForumPlugin
from .views import SearchView, ExtendedSearchView, SearchVariantsView
from .forms import SearchForm


class SearchPlugin(ForumPlugin):
    def search_url(self, thread):
        return self.reverse('search', thread.tree_id)

    def extended_search_url(self, thread):
        return self.reverse('extended_search', thread.tree_id)
        
    def init_core(self):
        self.core['search_form'] = SearchForm()
        self.urlizer['Thread_search_url'] = self.search_url
        self.core['search_variants'] = urls.reverse_lazy(
            self.site.app_name + ':search_variants')
        self.urlizer['Thread_extended_search_url'] = self.extended_search_url
        self.templates['search_post'] = 'forum/snippets/searched_post.haml'
        self.templates['search'] = 'forum/search.haml'
        self.templates['search_form'] = 'forum/search_form.haml'
        
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
            url(
                r'^search_variants/$',
                SearchVariantsView.as_view(),
                name='search_variants'),
        ]
