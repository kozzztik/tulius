import asyncio
from unittest import mock

import pytest
from django import urls
from django import http
from django.test import override_settings
from django.core import signals
from django.core.handlers import asgi as dj_asgi
from django.core.handlers import websocket

from tulius.websockets.asgi import asgi_handler
from tulius.websockets.asgi import utils
from tulius.websockets.asgi import connections


def setup_module(_):
    connections.ConnectionHandler.monkey_patch()


@pytest.mark.asyncio
async def test_unknown_scope_type():
    handler = asgi_handler.ASGIHandler()
    with pytest.raises(ValueError):
        await handler({'type': 'foobar'}, None, None)


class ASGIContext(utils.BaseASGIContext):
    async def send(self, data):
        await self._internal_send(data)

    async def receive(self):
        return await self._internal_read()


@pytest.mark.asyncio
async def test_lifespan():
    handler = asgi_handler.ASGIHandler()
    context = ASGIContext(handler, {'type': 'lifespan'})
    task = asyncio.create_task(context.run())
    await context.send({'type': 'lifespan.startup'})
    response = await context.receive()
    assert response['type'] == 'lifespan.startup.complete'
    # test shutdown
    await context.send({'type': 'lifespan.shutdown'})
    response = await context.receive()
    assert response['type'] == 'lifespan.shutdown.complete'
    # check task closed
    await task
    await context.closed


@pytest.mark.asyncio
async def test_body_abort():
    handler = asgi_handler.ASGIHandler()
    context = ASGIContext(handler, {'type': 'http'})
    await context.send({'type': 'http.disconnect'})
    await context.run()  # nothing fails
    await context.closed


@pytest.mark.asyncio
async def test_bad_scope():
    handler = asgi_handler.ASGIHandler()
    context = ASGIContext(handler, {'type': 'http'})
    await context.send({
        'type': 'http.request', 'body': b'foo', 'more_body': False,
    })
    await context.run()
    with pytest.raises(KeyError):
        await context.closed


class BadRequest(dj_asgi.ASGIRequest):
    def __init__(self, scope, body_file):
        raise dj_asgi.RequestDataTooBig()


@pytest.mark.asyncio
async def test_too_large_request():
    handler = utils.TestASGIHandler()
    handler.request_class = BadRequest
    context = utils.ASGIRequest(handler, {'type': 'http'})
    await context.run()  # nothing fails
    assert context.response.status_code == 413


def test_application():
    handler = asgi_handler.get_asgi_application()
    assert isinstance(handler, asgi_handler.ASGIHandler)


def _test_file_view(_):
    return http.FileResponse(streaming_content=[b'123'])


@websocket.websocket_view
def _ws_exc_view(_, __):
    raise ValueError()


@websocket.websocket_view
def _ws_cancel_view(_, __):
    raise asyncio.CancelledError()


@websocket.websocket_view
async def _ws_ping(_, ws: websocket.WebSocket):
    while True:
        data = await ws.receive_text()
        await ws.send_text(data + '_pong')


def _ws_view_proto(request):
    return websocket.HttpResponseUpgrade(
        handler=_ws_proto, sub_protocol=request.sub_protocols[-1])


async def _ws_proto(_, ws: websocket.WebSocket):
    while True:
        data = await ws.receive_text()
        await ws.send_text(data + '_pong')


def _ws_close(_):
    return websocket.HttpResponseWSClose(close_code=42, reason='foobar')


@websocket.websocket_view
async def _ws_close_after_read(_, ws: websocket.WebSocket):
    data = None
    try:
        data = await ws.receive_text()
        await ws.send_text(data + '_pong')
    finally:
        await ws.close(code=43, reason=data)


class UrlConf:
    urlpatterns = [
        urls.re_path(r'^file_response/$', _test_file_view),
        urls.re_path(r'^ws_exc/$', _ws_exc_view),
        urls.re_path(r'^ws_cancel/$', _ws_cancel_view),
        urls.re_path(r'^ws_ping/$', _ws_ping),
        urls.re_path(r'^ws_proto/$', _ws_view_proto),
        urls.re_path(r'^ws_close/$', _ws_close),
        urls.re_path(r'^ws_close_after_read/$', _ws_close_after_read),
    ]


@override_settings(ROOT_URLCONF=UrlConf)
@pytest.mark.asyncio
async def test_ping_pong():
    client = utils.AsyncClient()
    ws: utils.ASGIWebsocket = await client.ws('/ws_ping/')
    assert ws.connected.result() is True
    await ws.send_text('ping')
    result = await ws.receive_text()
    assert result == 'ping_pong'
    ws.close()
    assert ws.closed.done()


@override_settings(ROOT_URLCONF=UrlConf)
@pytest.mark.asyncio
async def test_file_chunks():
    class ChunkedHandler(utils.TestASGIHandler):
        chunk_size = 1
    client = utils.AsyncClient()
    client.handler.handler_class = ChunkedHandler
    response = await client.get('/file_response/')
    assert response.block_size == 1
    assert response.streaming is True


@pytest.mark.asyncio
async def test_websocket_on_http():
    client = utils.AsyncClient()
    ws = await client.ws('/file_response/')
    assert ws.connected.result() is False
    assert ws.closed.done()


@pytest.mark.asyncio
async def test_websocket_bad_request():
    class BadRequestHandler(utils.TestASGIHandler):
        request_class = BadRequest
    client = utils.AsyncClient()
    client.handler.handler_class = BadRequestHandler
    ws = await client.ws('/file_response/')
    assert ws.connected.result() is False
    assert ws.closed.done()


@override_settings(ROOT_URLCONF=UrlConf)
@pytest.mark.asyncio
async def test_websocket_exc():
    client = utils.AsyncClient(raise_request_exception=False)
    future = asyncio.Future()

    def receiver(**kwargs):
        future.set_result(None)

    signals.got_request_exception.connect(receiver)
    ws = None
    try:
        ws = await client.ws('/ws_exc/')
        assert ws.connected.result() is True
        await asyncio.wait([future, ws.closed], timeout=10)
        assert ws.closed.result() is None
        assert future.result() is None
    finally:
        signals.got_request_exception.disconnect(receiver)
        if ws:
            ws.close()


@override_settings(ROOT_URLCONF=UrlConf)
@pytest.mark.asyncio
async def test_websocket_timeout():
    client = utils.AsyncClient(raise_request_exception=False)
    receiver = mock.MagicMock()
    signals.got_request_exception.connect(receiver)
    ws = None
    try:
        ws = await client.ws('/ws_cancel/')
        assert ws.connected.result() is True
        assert ws.closed.result() is None
        assert not receiver.called
    finally:
        signals.got_request_exception.disconnect(receiver)
        if ws:
            ws.close()


@override_settings(ROOT_URLCONF=UrlConf)
@pytest.mark.asyncio
async def test_sub_protocols():
    client = utils.AsyncClient()
    ws: utils.ASGIWebsocket = await client.ws(
        '/ws_proto/', sub_protocols=['foo', 'bar'])
    try:
        assert ws.connected.result() is True
        assert ws.sub_protocol == 'bar'
    finally:
        ws.close()


@override_settings(ROOT_URLCONF=UrlConf)
@pytest.mark.asyncio
async def test_close_on_init():
    client = utils.AsyncClient()
    ws: utils.ASGIWebsocket = await client.ws('/ws_close/')
    try:
        assert ws.connected.result() is False
        assert ws.close_message['reason'] == 'foobar'
        assert ws.close_message['code'] == 42
    finally:
        ws.close()


@override_settings(ROOT_URLCONF=UrlConf)
@pytest.mark.asyncio
async def test_close_after_read():
    client = utils.AsyncClient()
    ws: utils.ASGIWebsocket = await client.ws('/ws_close_after_read/')
    try:
        assert ws.connected.result() is True
        await ws.send_text('ping')
        result = await ws.receive_text()
        assert result == 'ping_pong'
        with pytest.raises(asyncio.CancelledError):
            await ws.receive_text()
        assert ws.close_message['reason'] == 'ping'
        assert ws.close_message['code'] == 43
    finally:
        ws.close()
