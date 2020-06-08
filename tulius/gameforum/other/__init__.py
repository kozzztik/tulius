from tulius.forum.other import readmarks
from tulius.gameforum import threads


class ReadmarkAPI(readmarks.ReadmarkAPI, threads.BaseThreadAPI):
    pass
