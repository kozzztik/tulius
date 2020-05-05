from django.conf import settings

CHANNEL_PUBLIC = 'public'
CHANNEL_USER = 'user-{}'

USER_NEW_PM = 'new_pm'
USER_NEW_GAME_INVITATION = 'new_game_inv'


def make_channel_name(channel):
    return '{}_{}'.format(settings.ENV, channel)
