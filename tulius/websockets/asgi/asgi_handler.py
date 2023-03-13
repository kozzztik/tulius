import django
from django import http
from django import db

from django.core.handlers import asgi as dj_asgi
from tulius.websockets.asgi import connections


class HttpResponseUpgrade(http.HttpResponse):
    status_code = 101
    handler = None

    def __init__(self, handler, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.handler = handler


class ASGIHandler(dj_asgi.ASGIHandler):
    context_pool = None

    async def __call__(self, scope, receive, send):
        """
        Async entrypoint - parses the request and hands off to get_response.
        """
        if scope['type'] not in ['http', 'websocket', 'lifespan']:
            raise ValueError(
                "Django can only handle ASGI/HTTP connections, not %s."
                % scope["type"]
            )

        async with dj_asgi.ThreadSensitiveContext():
            try:
                await self.handle(scope, receive, send)
            finally:
                db.connections.close_context()

    async def handle(self, scope, receive, send):
        """
        Handles the ASGI request. Called via the __call__ method.
        """
        if scope['type'] == 'lifespan':
            return await self.handle_lifespan(scope, receive, send)
        # for backward capability. In websocket there is no "method" in scope
        if scope['type'] == 'websocket':
            scope['method'] = 'GET'
        # Receive the HTTP request body as a stream object.
        try:
            body_file = await self.read_body(receive)
        except dj_asgi.RequestAborted:
            return
        # Request is complete and can be served.
        try:
            dj_asgi.set_script_prefix(self.get_script_prefix(scope))
            await dj_asgi.sync_to_async(
                dj_asgi.signals.request_started.send, thread_sensitive=True
            )(sender=self.__class__, scope=scope)
            # Get the request and check for basic issues.
            request, error_response = self.create_request(scope, body_file)
            if request is None:
                await self.handle_response(
                    error_response, scope, receive, send)
                return
            # Get the response, using the async mode of BaseHandler.
            response = await self.get_response_async(request)
            response._handler_class = self.__class__
        finally:
            body_file.close()
        # Increase chunk size on file responses (ASGI servers handles low-level
        # chunking).
        if isinstance(response, dj_asgi.FileResponse):
            response.block_size = self.chunk_size
        # Send the response.
        await self.handle_response(response, scope, receive, send)

    async def handle_response(self, response, scope, receive, send):
        if scope['type'] == 'websocket':
            if isinstance(response, HttpResponseUpgrade):
                await response.handler(scope, receive, send)
            else:
                await send({'type': 'websocket.close'})
        else:
            await self.send_response(response, send)

    @staticmethod
    async def handle_lifespan(scope, receive, send):
        while True:
            message = await receive()
            if message['type'] == 'lifespan.startup':
                # Do some startup here!
                await send({'type': 'lifespan.startup.complete'})
            elif message['type'] == 'lifespan.shutdown':
                # Do some shutdown here!
                await send({'type': 'lifespan.shutdown.complete'})


def get_asgi_application():
    """
    The public interface to Django's ASGI support. Return an ASGI 3 callable.
    Avoids making django.core.handlers.ASGIHandler a public API, in case the
    internal implementation changes or moves in the future.
    """
    django.setup(set_prefix=False)
    connections.ConnectionHandler.monkey_patch()
    return ASGIHandler()
