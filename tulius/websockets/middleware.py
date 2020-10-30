from django.urls import resolve
from django.core.handlers import asgi

from tulius.websockets import connection


def websockets(app):
    async def asgi_app(scope, receive, send):
        if scope['type'] == 'lifespan':
            while True:
                message = await receive()
                if message['type'] == 'lifespan.startup':
                    # Do some startup here!
                    await send({'type': 'lifespan.startup.complete'})
                elif message['type'] == 'lifespan.shutdown':
                    # Do some shutdown here!
                    await send({'type': 'lifespan.shutdown.complete'})
        elif scope["type"] == "websocket":
            match = resolve(scope["path"])
            scope['method'] = 'GET'  # for backward capability
            request = asgi.ASGIRequest(scope, None)
            await match.func(
                request,
                connection.WebSocket(scope, receive, send),
                *match.args, **match.kwargs)
            return
        await app(scope, receive, send)
    return asgi_app
