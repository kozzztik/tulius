import django
from django import db
from django.core.handlers import asgi

from tulius.websockets.asgi import connections


class ASGIHandler(asgi.ASGIHandler):
    context_pool = None

    async def __call__(self, scope, receive, send):
        """
        Async entrypoint - parses the request and hands off to get_response.
        """
        if scope['type'] == 'lifespan':
            return await self.handle_lifespan(receive, send)
        if scope['type'] not in ['http', 'websocket']:
            raise ValueError(
                "Django can only handle ASGI/HTTP connections, not %s."
                % scope["type"]
            )

        async with asgi.ThreadSensitiveContext():
            try:
                await self.handle(scope, receive, send)
            finally:
                db.connections.close_context()

    async def run_get_response(self, request):
        try:
            return await super().run_get_response(request)
        finally:
            db.connections.close_context()

    @staticmethod
    async def handle_lifespan(receive, send):
        while True:
            message = await receive()
            if message['type'] == 'lifespan.startup':
                # Do some startup here!
                await send({'type': 'lifespan.startup.complete'})
            elif message['type'] == 'lifespan.shutdown':
                # Do some shutdown here!
                await send({'type': 'lifespan.shutdown.complete'})
                return


def get_asgi_application():
    """
    The public interface to Django's ASGI support. Return an ASGI 3 callable.
    Avoids making django.core.handlers.ASGIHandler a public API, in case the
    internal implementation changes or moves in the future.
    """
    django.setup(set_prefix=False)
    connections.ConnectionHandler.monkey_patch()
    return ASGIHandler()
