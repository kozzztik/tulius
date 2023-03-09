import asyncio
import json
import logging

from django.test import override_settings
from django import urls
from django import http
from django import db
from django.db import transaction
import pytest
from asgiref.sync import sync_to_async

from tulius.websockets.asgi import websocket
from tulius.websockets.asgi.asgi_handler import get_asgi_application


def _test_view(request, pk):
    with db.connection.cursor() as cursor:
        cursor.execute("SELECT %s", [pk])
        row = cursor.fetchone()
        return http.JsonResponse({
            'value': row[0],
            'connection': id(cursor.connection)
        })


@websocket.websocket_view
async def _test_web_socket_view(request, ws: websocket.WebSocket):
    def set_variable(pk):
        transaction.set_autocommit(False)
        with db.connection.cursor() as cursor:
            cursor.execute("SET @tmp = %s", [pk])

    def get_variable():
        with db.connection.cursor() as cursor:
            cursor.execute("SELECT @tmp")
            row = cursor.fetchone()
            return row[0]

    while True:
        try:
            text = await ws.receive_text()
            if text == "@GET":
                result = await sync_to_async(
                    get_variable, thread_sensitive=False)()
                await ws.send_text(result)
            else:
                await sync_to_async(set_variable, thread_sensitive=False)(text)
        except Exception as e:
            logging.exception(e)
            raise e


class UrlConf:
    urlpatterns = [
        urls.re_path(r'^test1/(?P<pk>\d+)/$', _test_view),
        urls.re_path(r'^ws/$', _test_web_socket_view),
    ]


class ASGIRequest:
    def __init__(self, app, scope, body):
        self.app = app
        self.scope = scope
        self.request_body = body
        self._request_body_send = False
        self.response_headers = {}
        self.response_body = b''
        self.response_status = None

    async def run(self):
        await self.app(self.scope, self._receive, self._send)

    async def _send(self, data):
        if data['type'] == 'http.response.start':
            self.response_status = data['status']
            self.response_headers = [
                (k.decode('utf-8'), v.decode('utf-8'))
                for k, v in data['headers']]
        elif data['type'] == 'http.response.body':
            self.response_body += data['body']

    async def _receive(self):
        if self._request_body_send:
            return {'type': 'http.disconnect'}
        self._request_body_send = True
        body = self.request_body
        if isinstance(body, str):
            body = body.encode('utf-8')
        return {
            'type': 'http.request',
            'body': body,
            'request_body': False,
        }

    def close(self):
        pass


class ASGIWebsocket(ASGIRequest):
    def __init__(self, app, scope, body):
        super().__init__(app, scope, body)
        self._send_queue = []
        self._receive_queue = []
        self._send_futures = []
        self._receive_futures = []
        self.connected = asyncio.Future()
        self.closed = asyncio.Future()

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
        asyncio.create_task(self.run())
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


class AsgiClient:
    def __init__(self):
        self.app = get_asgi_application()

    @staticmethod
    def _get_scope(path, headers=None, query_string='', ):
        headers = headers or {}
        headers.setdefault('HOST', '127.0.0.1')
        return {
            'asgi["version"]': '2.3',
            'http_version': '1.1',
            'path': path,
            'query_string': query_string,
            'headers': [
                (k.encode('utf-8'), v.encode('utf-8'))
                for k, v in headers.items()],
            'client': ('127.0.0.1', 0),
        }

    async def request(
            self, method, path,
            headers=None, query_string='', body=''):
        scope = self._get_scope(
            path, headers=headers, query_string=query_string)
        scope.update({
            'type': 'http',
            'scheme': 'http',
            'method': method,
        })
        context = ASGIRequest(self.app, scope, body)
        await context.run()
        return http.HttpResponse(
            status=context.response_status,
            headers=context.response_headers,
            content=context.response_body)

    async def get(self, path, headers=None, query_string='', body=''):
        return await self.request(
            'GET', path, headers=headers, query_string=query_string, body=body)

    def ws(self, path, headers=None, query_string='', body=''):
        scope = self._get_scope(
            path, headers=headers, query_string=query_string)
        scope['type'] = 'websocket'
        scope['scheme'] = 'ws'
        return ASGIWebsocket(self.app, scope, body)


@override_settings(ROOT_URLCONF=UrlConf)
def test_wsgi_connection_reusage(client):
    response = client.get('/test1/1/')
    data = json.loads(response.content)
    assert data['value'] == '1'
    conn1 = data['connection']
    response = client.get('/test1/2/')
    data = json.loads(response.content)
    assert data['value'] == '2'
    conn2 = data['connection']
    assert conn1 == conn2


@override_settings(ROOT_URLCONF=UrlConf)
@pytest.mark.asyncio
async def test_connection_reusage():
    client = AsgiClient()
    response = await client.get('/test1/1/')
    data = json.loads(response.content)
    assert data['value'] == '1'
    conn1 = data['connection']
    response = await client.get('/test1/2/')
    data = json.loads(response.content)
    assert data['value'] == '2'
    conn2 = data['connection']
    assert conn1 == conn2


@override_settings(ROOT_URLCONF=UrlConf)
@pytest.mark.asyncio
async def test_single_websocket():
    client = AsgiClient()
    async with client.ws('/ws/') as ws:
        await ws.send_text('1')
        await ws.send_text('@GET')
        result = await ws.receive_text()
        assert result == '1'


@override_settings(ROOT_URLCONF=UrlConf)
@pytest.mark.asyncio
async def test_parallel_websockets():
    client = AsgiClient()
    wss = []
    for i in range(10):
        ws = client.ws('/ws/')
        await ws.__aenter__()
        wss.append(ws)
    try:
        for i, ws in enumerate(wss):
            await ws.send_text(str(i))
        for ws in reversed(wss):
            await ws.send_text('@GET')
        results = []
        for ws in wss:
            results.append(await ws.receive_text())
    finally:
        for ws in wss:
            ws.close()
    assert results == [str(i) for i in range(10)]


@override_settings(ROOT_URLCONF=UrlConf)
@pytest.mark.asyncio
async def test_parallel_views():
    client = AsgiClient()
    wss = []
    for i in range(5):
        ws = client.ws('/ws/')
        await ws.__aenter__()
        wss.append(ws)
    try:
        views = [client.get(f'/test1/{i + len(wss)}/') for i in range(5)]
        for i, ws in enumerate(wss):
            await ws.send_text(str(i))
        for ws in reversed(wss):
            await ws.send_text('@GET')
        tasks = [ws.receive_text() for ws in wss] + views
        results = await asyncio.gather(*tasks)
        wss_results = results[:len(wss)]
        views = results[len(wss):]
        views_results = [json.loads(r.content)['value'] for r in views]
        results = wss_results + views_results
    finally:
        for ws in wss:
            ws.close()
    assert results == [str(i) for i in range(10)]
