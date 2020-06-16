from tulius.forum.other import readmarks
from tulius.gameforum.threads import api as threads


class ReadmarkAPI(readmarks.ReadmarkAPI, threads.BaseThreadAPI):
    pass
