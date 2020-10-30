import asyncio
import logging

import sentry_sdk
from redis_cache import RedisCache
from django.conf import settings
from django.db import transaction

from tulius.websockets import user_session


params = settings.CACHES['default'].copy()
if params['BACKEND'] != 'redis_cache.RedisCache':
    raise NotImplementedError()
redis_location = params.pop('LOCATION')
redis_cache = RedisCache(redis_location, params)


@transaction.non_atomic_requests
async def web_socket_view(request, socket, json_format=True):
    await socket.accept()
    session = user_session.UserSession(
        request, socket, redis_cache, json_format=json_format)
    try:
        await session.process()
    except asyncio.CancelledError:
        pass
    except Exception as e:
        logging.exception(e)
        await asyncio.get_event_loop().run_in_executor(
            None, sentry_sdk.capture_exception, e)
    finally:
        session.close()
        await socket.close()
