import asyncio
import logging

import sentry_sdk
from aiohttp import web
from django.conf import settings
from redis_cache import RedisCache
from tulius.websockets import user_session


class WebsocketHandler:
    def __init__(self):
        params = settings.CACHES['default'].copy()
        if params['BACKEND'] != 'redis_cache.RedisCache':
            raise NotImplementedError()
        redis_location = params.pop('LOCATION')
        self.redis_cache = RedisCache(redis_location, params)

    async def handler(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        session = user_session.UserSession(request, ws, self.redis_cache)
        try:
            await session.process()
        except Exception as e:
            logging.exception(e)
            await asyncio.get_event_loop().run_in_executor(
                sentry_sdk.capture_exception, e)
        finally:
            session.close()
        return ws


def setup_routes(app):
    app.add_routes([
        web.get(settings.WEBSOCKET_URL, WebsocketHandler().handler)])
