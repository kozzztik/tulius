from tulius.forum.other import readmarks
from tulius.forum.voting import views as voting
from tulius.gameforum.threads import api as threads
from tulius.gameforum.comments import api as comments


class ReadmarkAPI(readmarks.ReadmarkAPI, threads.BaseThreadAPI):
    pass


class VotingAPI(voting.VotingAPI, comments.CommentsBase):
    pass
