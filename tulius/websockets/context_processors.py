from django.conf import settings


def default(request):
    """
    Adds additional context variables to the default context.
    """
    protocol = 'wss://' if request.is_secure() else 'ws://'
    if settings.ENV == 'dev':
        uri = ''.join([
            protocol,
            settings.ASYNC_SERVER['host'],
            ':',
            str(settings.ASYNC_SERVER['port']),
            settings.WEBSOCKET_URL
        ])
    else:
        uri = protocol + request.get_host() + settings.WEBSOCKET_URL
    return {'WEBSOCKET_URI': uri}
