from .sites import GameForumSite
from tulius.forum.voting.plugin import VotingPlugin
from tulius.forum.readmarks.plugin import ReadMarksPlugin
from tulius.forum import FixesPlugin
from .gamecore import GamePlugin
from .trustmarks import TrustmarksPlugin
from .rights import GameRightsPlugin
from .search import GameSearchPlugin
from .threads import GameThreadsPlugin
from .comments import GameCommentsPlugin
from .online_status import GameOnlineStatusPlugin
from .sitemap import GameSitemapPlugin

GAMEFORUM_SITE_ID = 1

site = GameForumSite(name='gameforum', app_name='gameforum', site_id=GAMEFORUM_SITE_ID,
                 plugins=(
                          TrustmarksPlugin,
                          GameRightsPlugin,
                          GameThreadsPlugin,
                          GameCommentsPlugin,
                          VotingPlugin,
                          GameSearchPlugin,
                          ReadMarksPlugin,
                          GameOnlineStatusPlugin,
                          GamePlugin,
                          GameSitemapPlugin,
                          FixesPlugin
                          )
                 )