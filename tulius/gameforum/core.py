from tulius.forum import models
from tulius.gameforum import consts


def create_game_forum(user, variation):
    if variation.game:
        title = variation.game.name
    else:
        title = variation.name
    thread = models.Thread(
        title=title, user=user,
        access_type=models.THREAD_ACCESS_TYPE_OPEN,
        room=True, plugin_id=consts.GAME_FORUM_SITE_ID)
    thread.save()
    return thread
