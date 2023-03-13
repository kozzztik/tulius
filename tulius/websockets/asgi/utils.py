import asyncio

from django.test import client as django_client

from tulius.websockets.asgi import asgi_handler
from tulius.websockets.asgi import connections


class ASGIRequest:
    def __init__(self, app, scope):
        self.app = app
        self.scope = scope
        if "_body_file" in scope:
            self.body_file = scope.pop("_body_file")
        else:
            self.body_file = django_client.FakePayload("")
        self.response = None
        self._request_body_send = False
        self.request = None
        scope['_test_asgi_context'] = self

    async def run(self):
        await self.app(self.scope, self._receive, self._send)

    async def _send(self, data):
        data.asgi_request = self.request
        self.response = data

    async def _receive(self):
        if self._request_body_send:
            return {'type': 'http.disconnect'}
        self._request_body_send = True
        return {
            'type': 'http.request',
            'body': self.body_file.read(),
            'request_body': False,
        }


class ASGIWebsocket(ASGIRequest):
    def __init__(self, app, scope):
        super().__init__(app, scope)
        self._send_queue = []
        self._receive_queue = []
        self._send_futures = []
        self._receive_futures = []
        self.connected = asyncio.Future()
        self.closed = asyncio.Future()
        self.cookies = None

    async def run(self):
        try:
            await super().run()
        except Exception as e:
            self.close(e)
        else:
            self.close()

    async def _send(self, data):
        if data["type"] == "websocket.accept":
            self.connected.set_result(True)
            self.asgi_request = self.request
        elif data["type"] == "websocket.close":
            self.close()
        elif data["type"] == "websocket.send":
            if self._receive_futures:
                self._receive_futures.pop(0).set_result(data)
            else:
                self._receive_queue.append(data)

    async def _receive(self):
        if not self._request_body_send:
            self._request_body_send = True
            return {'type': 'websocket.connect'}
        self._request_body_send = True
        if self.closed.done():
            raise asyncio.CancelledError()
        if self._send_queue:
            return self._send_queue.pop(0)
        future = asyncio.Future()
        self._send_futures.append(future)
        await future
        return future.result()

    def close(self, exc=None):
        if self.closed.done():
            return
        if exc:
            self.closed.set_exception(exc)
        else:
            self.closed.set_result(None)
        for future in self._send_futures:
            future.cancel()
        for future in self._receive_futures:
            future.cancel()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.close()

    async def _internal_send(self, message):
        if self.closed.done():
            raise asyncio.CancelledError()
        if self._send_futures:
            self._send_futures.pop(0).set_result(message)
        else:
            self._send_queue.append(message)

    async def _internal_read(self):
        if self.closed.done():
            raise asyncio.CancelledError()
        if self._receive_queue:
            return self._receive_queue.pop(0)
        future = asyncio.Future()
        self._receive_futures.append(future)
        await future
        return future.result()

    async def send_text(self, text):
        await self._internal_send({"type": "websocket.receive", "text": text})

    async def receive_text(self):
        message = await self._internal_read()
        return message.get('bytes') or message.get('text')


class TestASGIHandler(asgi_handler.ASGIHandler):
    def __init__(self, enforce_csrf_checks=True):
        self.enforce_csrf_checks = enforce_csrf_checks
        super().__init__()

    async def send_response(self, response, send):
        await send(response)

    def create_request(self, scope, body_file):
        request, error_response = super().create_request(scope, body_file)
        request._dont_enforce_csrf_checks = not scope.scope.get(
            '_enforce_csrf_checks')
        scope.scope['_test_asgi_context'].request = request
        return request, error_response


class AsyncClientHandler:
    def __init__(self, enforce_csrf_checks=True):
        self.enforce_csrf_checks = enforce_csrf_checks
        connections.ConnectionHandler.monkey_patch()

    async def __call__(self, scope):
        app = TestASGIHandler(self.enforce_csrf_checks)
        if scope['type'] == 'websocket':
            context = ASGIWebsocket(app, scope)
            asyncio.create_task(context.run())
            await context.connected
            return context
        context = ASGIRequest(app, scope)
        await asyncio.create_task(context.run())
        return context.response


class AsyncClient(django_client.AsyncClient):
    def __init__(
            self, enforce_csrf_checks=False, raise_request_exception=True,
            **defaults):
        super().__init__(
            enforce_csrf_checks=enforce_csrf_checks,
            raise_request_exception=raise_request_exception, **defaults)
        self.handler = AsyncClientHandler(enforce_csrf_checks)

    def ws(self, path, secure=False, **extra):
        """Construct a GET request."""
        return self.generic(
            "WS",
            path,
            secure=secure,
            **extra,
        )

    def _base_scope(self, **request):
        scope = super()._base_scope(**request)
        if request['method'] == 'WS':
            scope['type'] = 'websocket'
            scope['scheme'] = 'ws'
            scope.pop('method')
        return scope
