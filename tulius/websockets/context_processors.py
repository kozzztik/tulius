from django import urls


def default(request, json_format=False):
    """
    Adds additional context variables to the default context.
    """
    web_url = urls.reverse('websockets:ws') if json_format \
        else urls.reverse('websockets:old')
    protocol = 'wss://' if request.is_secure() else 'ws://'
    return {'WEBSOCKET_URI': protocol + request.get_host() + web_url}
