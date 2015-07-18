from tulius.forum import site
from tulius.gameforum import site as game_forum
from djfw.flatpages.sitemaps import FlatPageSitemap
from djfw.news.sitemap import NewsSitemap
from tulius.stories.sitemap import StoriesSitemap
from tulius.games.sitemap import GamesSitemap

sitemaps = {
            'forum': site.core['sitemap'](),
            'gameforum': game_forum.core['sitemap'](),
            'flatpages': FlatPageSitemap,
            'news': NewsSitemap,
            'stories': StoriesSitemap,
            'games': GamesSitemap,
            }