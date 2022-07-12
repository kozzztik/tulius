import asyncio

import sentry_sdk
from aiohttp.web import WebSocketResponse
from redis_cache import RedisCache
from django_asyncio.aiohttp_handler import websocket_view
from django.conf import settings
from django.db import transaction

from tulius.websockets import user_session


params = settings.CACHES['default'].copy()
if params['BACKEND'] != 'redis_cache.RedisCache':
    raise NotImplementedError()
redis_location = params.pop('LOCATION')
redis_cache = RedisCache(redis_location, params)


@transaction.non_atomic_requests
@websocket_view
async def web_socket_view(request, ws: WebSocketResponse, json_format=True):
    session = user_session.UserSession(
        request, ws, redis_cache, json_format=json_format)
    try:
        await session.process()
    except asyncio.CancelledError:
        pass
    except Exception as e:
        await asyncio.get_event_loop().run_in_executor(
            None, sentry_sdk.capture_exception, e)
        raise
    finally:
        session.close()
