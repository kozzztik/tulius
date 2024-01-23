import json
import logging

from django.core.cache.backends.redis import RedisCache
from django.conf import settings
from django.db import transaction
from redis import asyncio as aioredis

from django_h2.sse import SSEResponse

from tulius.websockets import user_session
from tulius.websockets.asgi import websocket
from tulius.websockets import consts

logger = logging.getLogger('async_app')

params = settings.CACHES['default'].copy()
if params['BACKEND'] != 'django.core.cache.backends.redis.RedisCache':
    raise NotImplementedError()
redis_location = params.pop('LOCATION')
redis_cache = RedisCache(redis_location, params)


@transaction.non_atomic_requests
@websocket.websocket_view
async def web_socket_view(request, ws: websocket.WebSocket, json_format=True):
    session = user_session.UserSession(
        request, ws, redis_cache, json_format=json_format)
    try:
        await session.process()
    finally:
        await session.close()


class RedisChannel:
    def __init__(self, user, channel_names, request):
        self.channel_names = channel_names
        self.response = SSEResponse(request, handler=self.handler())
        self.user = user

    async def handler(self):
        redis = aioredis.from_url(settings.REDIS_LOCATION)
        pubsub = redis.pubsub()
        await pubsub.subscribe(
            **{
                consts.make_channel_name(name): self._get_message
                for name in self.channel_names
            }
        )
        await pubsub.run(
            exception_handler=self._pubsub_exc_handler, poll_timeout=30)

    @staticmethod
    def _pubsub_exc_handler(e, *args):
        logging.exception(e)

    async def _get_message(self, message):
        logger.debug('User %s message %s', self.user, message)
        message = json.loads(message['data'])
        direct = message.pop('.direct')
        name = message.pop('.namespaced')
        pk = message.pop('id', None)
        if direct:
            await self.response.send_event(
                name, json.dumps(message), event_id=pk)


def pm_messages(request):
    names = [consts.CHANNEL_PUBLIC]
    if request.user.is_authenticated:
        names.append(consts.CHANNEL_USER.format(request.user.id))
    channel = RedisChannel(request.user, names, request)
    return channel.response
