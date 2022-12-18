"""
This file is from https://vk.com/@python_django_ru-veb-sokety-v-django-31
https://gist.github.com/alex-oleshkevich/
77a9386cc01c730eccaa45d366bae459#file-connection-py
"""
import json
import typing as t
import functools

from django.core import exceptions

from tulius.websockets.asgi import asgi_handler


class State:
    CONNECTING = 1
    CONNECTED = 2
    DISCONNECTED = 3


class SendEvent:
    """Lists events that application can send.
    ACCEPT - Sent by the application when it wishes to accept an incoming
    connection.
    SEND - Sent by the application to send a data message to the client.
    CLOSE - Sent by the application to tell the server to close the connection.
        If this is sent before the socket is accepted, the server must close
        the connection with a HTTP 403 error code (Forbidden), and not complete
        the WebSocket handshake; this may present on some browsers as
        a different WebSocket error code (such as 1006, Abnormal Closure).
    """

    ACCEPT = "websocket.accept"
    SEND = "websocket.send"
    CLOSE = "websocket.close"


class ReceiveEvent:
    """Enumerates events that application can receive from protocol server.
    CONNECT - Sent to the application when the client initially
        opens  a connection and is about to finish the WebSocket handshake.
        This message must be responded to with either an Accept message or a
        Close message before the socket will pass websocket.receive messages.
    RECEIVE - Sent to the application when a data message is received from the
    client.
    DISCONNECT - Sent to the application when either connection to the client
        is lost, either from the client closing the connection,
        the server closing the connection, or loss of the socket.
    """

    CONNECT = "websocket.connect"
    RECEIVE = "websocket.receive"
    DISCONNECT = "websocket.disconnect"


class WebSocket:
    def __init__(self, request):
        transport = getattr(request, 'asgi', None)
        if transport is None:
            raise exceptions.ImproperlyConfigured(
                'Recieved websocket request out of ASGI protocol')
        if transport.ws:
            raise exceptions.ImproperlyConfigured(
                'Websocket connection already created')
        if transport.scope['type'] != 'websocket':
            raise exceptions.ValidationError(
                'User does not request websocket')
        transport.ws = self
        self._scope = transport.scope
        self._receive = transport.receive
        self._send = transport.send
        self._state = State.CONNECTING

    async def accept(self, subprotocol: str = None):
        """Accept connection.
        :param subprotocol: The subprotocol the server wishes to accept.
        :type subprotocol: str, optional
        """
        await self.send({"type": SendEvent.ACCEPT, "subprotocol": subprotocol})

    async def close(self, code: int = 1000):
        await self.send({"type": SendEvent.CLOSE, "code": code})

    @property
    def closed(self):
        return self._state == State.DISCONNECTED

    async def send(self, message: t.Mapping):
        if self._state == State.DISCONNECTED:
            raise RuntimeError("WebSocket is disconnected.")

        if self._state == State.CONNECTING:
            assert message["type"] in {SendEvent.ACCEPT, SendEvent.CLOSE}, (
                'Could not write event "%s" into socket in connecting state.'
                % message["type"]
            )
            if message["type"] == SendEvent.CLOSE:
                self._state = State.DISCONNECTED
            else:
                self._state = State.CONNECTED

        elif self._state == State.CONNECTED:
            assert message["type"] in {SendEvent.SEND, SendEvent.CLOSE}, (
                'Connected socket can send "%s" and "%s" events, not "%s"'
                % (SendEvent.SEND, SendEvent.CLOSE, message["type"])
            )
            if message["type"] == SendEvent.CLOSE:
                self._state = State.DISCONNECTED

        await self._send(message)

    async def receive(self):
        if self._state == State.DISCONNECTED:
            raise RuntimeError("WebSocket is disconnected.")

        message = await self._receive()

        if self._state == State.CONNECTING:
            assert message["type"] == ReceiveEvent.CONNECT, (
                'WebSocket is in connecting state but received "%s" event'
                % message["type"]
            )
            self._state = State.CONNECTED

        elif self._state == State.CONNECTED:
            assert message["type"] in {
                ReceiveEvent.RECEIVE, ReceiveEvent.DISCONNECT}, (
                'WebSocket is connected but received invalid event "%s".'
                % message["type"]
            )
            if message["type"] == ReceiveEvent.DISCONNECT:
                self._state = State.DISCONNECTED

        return message

    async def receive_json(self) -> t.Any:
        message = await self.receive()
        if message["type"] == ReceiveEvent.DISCONNECT:
            return None
        self._test_if_can_receive(message)
        return json.loads(message["text"])

    async def receive_jsonb(self) -> t.Any:
        message = await self.receive()
        if message["type"] == ReceiveEvent.DISCONNECT:
            return None
        self._test_if_can_receive(message)
        return json.loads(message["bytes"].decode())

    async def receive_text(self) -> t.Optional[str]:
        message = await self.receive()
        if message["type"] == ReceiveEvent.DISCONNECT:
            return None
        self._test_if_can_receive(message)
        return message["text"]

    async def receive_bytes(self) -> t.Optional[bytes]:
        message = await self.receive()
        if message["type"] == ReceiveEvent.DISCONNECT:
            return None
        self._test_if_can_receive(message)
        return message["bytes"]

    async def send_json(self, data: t.Any, **dump_kwargs):
        data = json.dumps(data, **dump_kwargs)
        await self.send({"type": SendEvent.SEND, "text": data})

    async def send_jsonb(self, data: t.Any, **dump_kwargs):
        data = json.dumps(data, **dump_kwargs)
        await self.send({"type": SendEvent.SEND, "bytes": data.encode()})

    async def send_text(self, text: str):
        await self.send({"type": SendEvent.SEND, "text": text})

    async def send_bytes(self, text: t.Union[str, bytes]):
        if isinstance(text, str):
            text = text.encode()
        await self.send({"type": SendEvent.SEND, "bytes": text})

    def _test_if_can_receive(self, message: t.Mapping):
        assert message["type"] == ReceiveEvent.RECEIVE, (
            'Invalid message type "%s". Was connection accepted?' %
            message["type"]
        )


def websocket_view(func):
    async def websocket_handler(request, ws, *args, **kwargs):
        await ws.accept()
        try:
            return await func(request, ws, *args, **kwargs)
        finally:
            if not ws.closed:
                await ws.close()

    @functools.wraps(func)
    def wrapper(request, *args, **kwargs):
        ws = WebSocket(request)
        request.asgi.ws = ws
        return asgi_handler.HttpResponseUpgrade(
            functools.partial(websocket_handler, request, ws, *args, **kwargs))

    wrapper.websocket_wrapper = True
    return wrapper
