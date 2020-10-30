from django.urls import resolve
from django.core.handlers import asgi

from tulius.websockets import connection


def websockets(app):
    async def asgi_app(scope, receive, send):
        if scope["type"] == "websocket":
            match = resolve(scope["raw_path"])
            request = asgi.ASGIRequest(scope, None)
            await match.func(
                request,
                connection.WebSocket(scope, receive, send),
                *match.args, **match.kwargs)
            return
        await app(scope, receive, send)
    return asgi_app
