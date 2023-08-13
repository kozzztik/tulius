import pytest
from django.core import exceptions

from tulius.websockets.asgi import websocket


@pytest.mark.asyncio
async def test_accept_ws_twice():
    async def _receive():
        return {'type': 'websocket.connect'}

    async def _send(_):
        pass

    ws = websocket.WebSocket(_receive, _send)
    await ws.accept(websocket.HttpResponseUpgrade(handler=None))
    with pytest.raises(websocket.WSProtoException) as exc:
        await ws.accept(websocket.HttpResponseUpgrade(handler=None))
    assert exc.value.args[0] == 'Websocket can be accepted only once'


@pytest.mark.asyncio
async def test_accept_headers():
    data = []

    async def _receive():
        return {'type': 'websocket.connect'}

    async def _send(message):
        data.append(message)

    response = websocket.HttpResponseUpgrade(handler=None)
    response.headers['Foo'] = 'Bar'
    ws = websocket.WebSocket(_receive, _send)
    await ws.accept(response)
    assert len(data) == 1
    headers = data[0]['headers']
    assert len(headers) == 2
    assert headers[1] == (b'foo', b'Bar')  # lower cased binary


@pytest.mark.asyncio
async def test_operation_without_accept():
    data = []

    async def _send(message):
        data.append(message)

    ws = websocket.WebSocket(None, _send)
    with pytest.raises(websocket.WSProtoException) as exc:
        await ws.send({})
    assert exc.value.args[0] == 'Websocket needs to be accepted before send'
    with pytest.raises(websocket.WSProtoException) as exc:
        await ws.receive()
    assert exc.value.args[0] == \
        'Websocket needs to be accepted before receive data'
    assert not data
    await ws.close()
    assert ws.closed
    assert len(data) == 1
    assert data[0]['type'] == 'websocket.close'


@pytest.mark.asyncio
async def test_operation_on_closed_ws():
    data = []

    async def _receive():
        return {'type': 'websocket.connect'}

    async def _send(message):
        data.append(message)

    ws = websocket.WebSocket(_receive, _send)
    await ws.accept(websocket.HttpResponseUpgrade(handler=None))
    await ws.close()

    with pytest.raises(websocket.WSProtoException) as exc:
        await ws.send({})
    assert exc.value.args[0] == 'WebSocket is closed'
    with pytest.raises(websocket.WSProtoException) as exc:
        await ws.receive()
    assert exc.value.args[0] == 'WebSocket is closed'
    assert ws.closed
    assert len(data) == 2
    assert data[0]['type'] == 'websocket.accept'
    assert data[1]['type'] == 'websocket.close'


@pytest.mark.asyncio
async def test_read_unknown_message():
    in_data = [{'type': 'websocket.connect'}, {'type': 'websocket.foo'}]

    async def _receive():
        return in_data.pop(0)

    async def _send(_):
        pass

    ws = websocket.WebSocket(_receive, _send)
    await ws.accept(websocket.HttpResponseUpgrade(handler=None))
    with pytest.raises(websocket.WSProtoException) as exc:
        await ws.receive()
    assert exc.value.args[0].startswith('Wrong websocket receive message type')


@pytest.mark.asyncio
async def test_read_on_close():
    in_data = [
        {'type': 'websocket.receive', 'text': 'foo'},
        {'type': 'websocket.disconnect'},
    ]

    async def _receive():
        return in_data.pop(0)

    async def _send(_):
        pass

    ws = websocket.WebSocket(_receive, _send)
    await ws.accept(websocket.HttpResponseUpgrade(handler=None))
    message = await ws.receive_text()
    assert message == 'foo'
    with pytest.raises(exceptions.RequestAborted):
        await ws.receive_text()


@pytest.mark.asyncio
async def test_read_json_binary_and_text():
    in_data = [
        {'type': 'websocket.receive', 'text': '{"foo": "bar"}'},
        {'type': 'websocket.receive', 'bytes': b'{"bar": "foo"}'},
    ]

    async def _receive():
        return in_data.pop(0)

    async def _send(_):
        pass

    ws = websocket.WebSocket(_receive, _send)
    await ws.accept(websocket.HttpResponseUpgrade(handler=None))
    message = await ws.receive_json()
    assert message == {'foo': 'bar'}
    message = await ws.receive_json()
    assert message == {'bar': 'foo'}


@pytest.mark.asyncio
async def test_read_text_binary_and_text():
    in_data = [
        {'type': 'websocket.receive', 'text': 'foo'},
        {'type': 'websocket.receive', 'bytes': b'bar'},
    ]

    async def _receive():
        return in_data.pop(0)

    async def _send(_):
        pass

    ws = websocket.WebSocket(_receive, _send)
    await ws.accept(websocket.HttpResponseUpgrade(handler=None))
    message = await ws.receive_text()
    assert message == 'foo'
    message = await ws.receive_text()
    assert message == 'bar'


@pytest.mark.asyncio
async def test_read_bytes_binary_and_text():
    in_data = [
        {'type': 'websocket.receive', 'text': 'foo'},
        {'type': 'websocket.receive', 'bytes': b'bar'},
    ]

    async def _receive():
        return in_data.pop(0)

    async def _send(_):
        pass

    ws = websocket.WebSocket(_receive, _send)
    await ws.accept(websocket.HttpResponseUpgrade(handler=None))
    message = await ws.receive_bytes()
    assert message == b'foo'
    message = await ws.receive_bytes()
    assert message == b'bar'


@pytest.mark.asyncio
async def test_send_json():
    data = []

    async def _receive():
        return {'type': 'websocket.connect'}

    async def _send(message):
        data.append(message)
    ws = websocket.WebSocket(_receive, _send)
    await ws.accept(websocket.HttpResponseUpgrade(handler=None))
    await ws.send_json({'foo': 'bar'})
    assert len(data) == 2
    assert data[0]['type'] == 'websocket.accept'
    assert data[1]['type'] == 'websocket.send'
    assert data[1]['text'] == '{"foo": "bar"}'


@pytest.mark.asyncio
async def test_send_text():
    data = []

    async def _receive():
        return {'type': 'websocket.connect'}

    async def _send(message):
        data.append(message)
    ws = websocket.WebSocket(_receive, _send)
    await ws.accept(websocket.HttpResponseUpgrade(handler=None))
    with pytest.raises(websocket.WSProtoException):
        await ws.send_text(b'bar')
    await ws.send_text('foo')
    assert len(data) == 2
    assert data[0]['type'] == 'websocket.accept'
    assert data[1]['type'] == 'websocket.send'
    assert data[1]['text'] == 'foo'


@pytest.mark.asyncio
async def test_send_bytes():
    data = []

    async def _receive():
        return {'type': 'websocket.connect'}

    async def _send(message):
        data.append(message)
    ws = websocket.WebSocket(_receive, _send)
    await ws.accept(websocket.HttpResponseUpgrade(handler=None))
    with pytest.raises(websocket.WSProtoException):
        await ws.send_bytes('bar')
    await ws.send_bytes(b'foo')
    assert len(data) == 2
    assert data[0]['type'] == 'websocket.accept'
    assert data[1]['type'] == 'websocket.send'
    assert data[1]['bytes'] == b'foo'


@pytest.mark.asyncio
async def test_accept_wrong_order():
    """ Some servers send connect on handshake finish. """
    data = []

    async def _receive():
        if not data:
            raise ValueError()
        return {'type': 'websocket.connect'}

    async def _send(message):
        data.append(message)

    ws = websocket.WebSocket(_receive, _send)
    await ws.accept(websocket.HttpResponseUpgrade(handler=None))
    assert len(data) == 1
    assert data[0]['type'] == 'websocket.accept'
