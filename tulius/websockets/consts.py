from django.conf import settings

CHANNEL_PUBLIC = 'public'
CHANNEL_USER = 'user-{}'

USER_NEW_PM = 'new_pm'
USER_NEW_GAME_INVITATION = 'new_game_inv'

THREAD_COMMENTS_NEW_COMMENT = 'new_comment'
THREAD_COMMENTS_CHANNEL = 'forum_thread_comments_{thread_id}'


def make_channel_name(channel):
    return '{}_{}'.format(settings.ENV, channel)
