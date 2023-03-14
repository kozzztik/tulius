import asyncio
import json
import logging
from unittest import mock

from django.test import override_settings
from django import urls
from django import http
from django import db
from django.db import transaction
import pytest
from asgiref.sync import sync_to_async

from tulius.websockets.asgi import websocket
from tulius.websockets.asgi.utils import AsyncClient
from tulius.websockets.asgi import connections


def _test_view(_, pk):
    with db.connection.cursor() as cursor:
        cursor.execute("SELECT %s", [pk])
        row = cursor.fetchone()
        return http.JsonResponse({
            'value': row[0],
            'connection': id(cursor.connection)
        })


@websocket.websocket_view
async def _test_web_socket_view(_, ws: websocket.WebSocket):
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
    client = AsyncClient()
    await sync_to_async(db.connections.close_all)()
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
    client = AsyncClient()
    async with await client.ws('/ws/') as ws:
        await ws.send_text('1')
        await ws.send_text('@GET')
        result = await ws.receive_text()
        assert result == '1'


@override_settings(ROOT_URLCONF=UrlConf)
@pytest.mark.asyncio
async def test_parallel_websockets():
    client = AsyncClient()
    wss = []
    for i in range(10):
        ws = await client.ws('/ws/')
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
    client = AsyncClient()
    wss = []
    for i in range(5):
        ws = await client.ws('/ws/')
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


def test_missing_connection():
    handler = connections.ConnectionHandler()
    with pytest.raises(handler.exception_class):
        handler['foobar']


def test_closing_connections_in_pool():
    handler = connections.ConnectionHandler()
    handler['default'] = conn = mock.MagicMock()
    handler.close_context()
    handler.close_all()
    assert conn.close.called


def test_closing_connections_in_context():
    handler = connections.ConnectionHandler()
    handler['default'] = conn = mock.MagicMock()
    handler.close_all()
    assert conn.close.called
