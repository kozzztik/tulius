from django.core.cache.backends.redis import RedisCache
from django.conf import settings
from django.db import transaction

from tulius.websockets import user_session
from tulius.websockets.asgi import websocket

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
