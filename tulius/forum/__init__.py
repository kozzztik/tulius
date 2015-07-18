from .sites import ForumSite
from .threads.plugin import ThreadsPlugin
from .search.plugin import SearchPlugin
from .comments.plugin import CommentsPlugin
from .fixes.plugin import FixesPlugin
from .voting.plugin import VotingPlugin
from .readmarks.plugin import ReadMarksPlugin
from .rights.plugin import RightsPlugin
from .online_status import OnlineStatusPlugin
from .sitemap import SitemapPlugin
from .collapse_threads import CollapsingThreadsPlugin

site = ForumSite(
                 plugins=(
                          RightsPlugin,
                          ThreadsPlugin,
                          CommentsPlugin,
                          VotingPlugin,
                          SearchPlugin,
                          ReadMarksPlugin,
                          OnlineStatusPlugin,
                          SitemapPlugin,
                          FixesPlugin,
                          CollapsingThreadsPlugin
                          )
                 )