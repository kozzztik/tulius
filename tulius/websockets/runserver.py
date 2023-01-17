import asyncio
import logging

from aiohttp import web
from aiohttp.http import WSMsgType
from django.contrib.staticfiles import handlers as static_handlers
from django.core.management.commands import runserver as dj_runserver

from tulius.websockets.asgi import asgi_handler

logger = logging.getLogger('django.server')


class ASGIRequestHandler:
    _response_start = None
    _response_body = None
    _ws = None

    def __init__(self, request):
        self.body_read = False
        self.request = request
        if request.headers.get('Upgrade') == 'websocket':
            connection_type = 'websocket'
        else:
            connection_type = 'http'
        self.scope = {
            'type': connection_type,
            'root_path': '',
            'path': request.path,
            'raw_path': request.raw_path,
            'method': request.method,
            'query_string': request.query_string,
            'client': request._transport_peername,
            'server': ('host', 0),
            'headers': [(n.lower(), v) for n, v in request.raw_headers],
        }

    async def receive(self):
        if not self.body_read:
            self.body_read = True
            data = await self.request.read()
            if self.scope['type'] == 'websocket':
                msg_type = 'websocket.connect'
            else:
                msg_type = 'body'
            return {
                'type': msg_type,
                'body': data,
            }
        if self._ws is not None:
            msg = await self._ws.receive()
            if msg.type in (
                    WSMsgType.CLOSE, WSMsgType.CLOSING, WSMsgType.CLOSED):
                return {'type': 'websocket.disconnect'}
            return {
                'type': 'websocket.receive',
                'text': msg.data,
            }
        return {'type': 'body end'}

    async def send(self, context):
        if context['type'] == 'http.response.start':
            self._response_start = context
        elif context['type'] == 'http.response.body':
            if not self._response_body:
                self._response_body = []
            if 'body' in context:
                self._response_body.append(context['body'])
        elif context['type'] == 'websocket.accept':
            self._ws = web.WebSocketResponse()
            await self._ws.prepare(self.request)
        elif context['type'] == 'websocket.send':
            await self._ws.send_str(context['text'])
        elif context['type'] == 'websocket.close':
            await self._ws.close()
        else:
            raise NotImplementedError()

    async def handle(self, application):
        try:
            await application(self.scope, self.receive, self.send)
            if self._ws is not None:
                return self._ws
            return web.Response(
                status=self._response_start['status'],
                headers=[
                    (n.decode('ascii'), v.decode('latin1'))
                    for n, v in self._response_start['headers']],
                body=b''.join(self._response_body)
            )
        except Exception as e:
            logger.exception(e)
        finally:
            if self._response_start:
                status_code = self._response_start.get('status', 500)
            else:
                status_code = 500
            if status_code >= 500:
                level = logger.error
            elif status_code >= 400:
                level = logger.warning
            else:
                level = logger.info

            level('%s %s', self.request.path, status_code)


class ASGIServer:
    def __init__(self, server_address, handler, ipv6):
        self.app = web.Application()
        self.asgi_application = asgi_handler.get_asgi_application()
        self.server_address = server_address
        self.app.add_routes([
            web.get('/{tail:.*}', self.aiohttp_handler),
            web.post('/{tail:.*}', self.aiohttp_handler),
            web.put('/{tail:.*}', self.aiohttp_handler),
            web.options('/{tail:.*}', self.aiohttp_handler),
        ])

    def set_app(self, wsgi_handler):
        if isinstance(wsgi_handler, static_handlers.StaticFilesHandler):
            self.asgi_application = static_handlers.ASGIStaticFilesHandler(
                self.asgi_application
            )

    def serve_forever(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        web.run_app(
            self.app,
            host=self.server_address[0],
            port=self.server_address[1],
            print=None,
        )

    async def aiohttp_handler(self, request):
        handler = ASGIRequestHandler(request)
        return await handler.handle(self.asgi_application)


def patch():
    dj_runserver.Command.server_cls = ASGIServer
