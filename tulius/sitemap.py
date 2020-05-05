from django.apps import apps

from djfw.flatpages.sitemaps import FlatPageSitemap
from djfw.news.sitemap import NewsSitemap
from tulius.stories.sitemap import StoriesSitemap
from tulius.games.sitemap import GamesSitemap


sitemaps = {
    'forum': apps.get_app_config('forum').site.core['sitemap'](),
    'gameforum': apps.get_app_config('gameforum').site.core['sitemap'](),
    'flatpages': FlatPageSitemap,
    'news': NewsSitemap,
    'stories': StoriesSitemap,
    'games': GamesSitemap,
}
