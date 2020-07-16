from djfw.flatpages.sitemaps import FlatPageSitemap
from djfw.news.sitemap import NewsSitemap
from tulius.stories.sitemap import StoriesSitemap
from tulius.games.sitemap import GamesSitemap
from tulius.forum.other import sitemap as forum_sitemap
from tulius.gameforum.other import sitemap as game_forum_sitemap


sitemaps = {
    'forum': forum_sitemap.ForumSitemap(),
    'gameforum': game_forum_sitemap.GameForumSitemap(),
    'flatpages': FlatPageSitemap,
    'news': NewsSitemap,
    'stories': StoriesSitemap,
    'games': GamesSitemap,
}
