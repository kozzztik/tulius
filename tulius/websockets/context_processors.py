from django.conf import settings


def default(request, json_format=False):
    """
    Adds additional context variables to the default context.
    """
    web_url = settings.WEBSOCKET_URL_NEW if json_format \
        else settings.WEBSOCKET_URL
    protocol = 'wss://' if request.is_secure() else 'ws://'
    if settings.ENV == 'dev':
        uri = ''.join([
            protocol,
            settings.ASYNC_SERVER['host'],
            ':',
            str(settings.ASYNC_SERVER['port']),
            web_url
        ])
    else:
        uri = protocol + request.get_host() + web_url
    return {'WEBSOCKET_URI': uri}
