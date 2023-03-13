import asyncio

import pytest
from django import urls
from django import http
from django.test import override_settings
from django.core.handlers import asgi as dj_asgi

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


class UrlConf:
    urlpatterns = [
        urls.re_path(r'^file_response/$', _test_file_view),
    ]


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
