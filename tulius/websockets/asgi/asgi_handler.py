import django
from django import http
from django.core.handlers import asgi as dj_asgi


class HttpResponseUpgrade(http.HttpResponse):
    status_code = 101


class ASGITransport:
    scope = None
    receive = None
    send = None
    ws = None

    def __init__(self, scope, receive, send):
        self.scope = scope
        self.receive = receive
        self.send = send


class ASGIRequest(dj_asgi.ASGIRequest):
    asgi = None
    scope_type = None

    def __init__(self, transport: ASGITransport, body_file):
        self.asgi = transport
        # for backward capability. In websocket there is no "method" in scope
        if transport.scope['type'] == 'websocket':
            transport.scope['method'] = 'GET'
        transport.scope.setdefault('method', 'GET')
        super().__init__(transport.scope, body_file)


class ASGIHandler(dj_asgi.ASGIHandler):
    request_class = ASGIRequest

    async def __call__(self, scope, receive, send):
        """
        Async entrypoint - parses the request and hands off to get_response.
        """
        transport = ASGITransport(scope, receive, send)
        if scope['type'] == 'lifespan':
            return await self.handle_lifespan(transport)
        if scope['type'] not in ['http', 'websocket']:
            raise ValueError(
                'Django can only handle ASGI/HTTP connections, not %s.'
                % scope['type']
            )
        # Receive the HTTP request body as a stream object.
        try:
            body_file = await self.read_body(receive)
        except dj_asgi.RequestAborted:
            return
        # Request is complete and can be served.
        dj_asgi.set_script_prefix(self.get_script_prefix(scope))
        await dj_asgi.sync_to_async(
            dj_asgi.signals.request_started.send, thread_sensitive=True
        )(sender=self.__class__, scope=scope)
        # Get the request and check for basic issues.
        request, error_response = self.create_request(transport, body_file)
        if request is None:
            await self.send_response(error_response, send)
            return
        # Get the response, using the async mode of BaseHandler.
        response = await self.get_response_async(request)
        response._handler_class = self.__class__
        # Increase chunk size on file responses (ASGI servers handles low-level
        # chunking).
        if isinstance(response, dj_asgi.FileResponse):
            response.block_size = self.chunk_size
        # Send the response.
        await self.send_response(response, send)

    @staticmethod
    async def handle_lifespan(transport):
        while True:
            message = await transport.receive()
            if message['type'] == 'lifespan.startup':
                # Do some startup here!
                await transport.send({'type': 'lifespan.startup.complete'})
            elif message['type'] == 'lifespan.shutdown':
                # Do some shutdown here!
                await transport.send({'type': 'lifespan.shutdown.complete'})

    async def send_response(self, response, send):
        if isinstance(response, HttpResponseUpgrade):
            # websocket view already send reponse, nothing needs to be done.
            return
        return await super().send_response(response, send)


def get_asgi_application():
    """
    The public interface to Django's ASGI support. Return an ASGI 3 callable.

    Avoids making django.core.handlers.ASGIHandler a public API, in case the
    internal implementation changes or moves in the future.
    """
    django.setup(set_prefix=False)
    return ASGIHandler()
