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

    async def handler(self, request, json_format=False):
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        session = user_session.UserSession(
            request, ws, self.redis_cache, json_format)
        try:
            await session.process()
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logging.exception(e)
            await asyncio.get_event_loop().run_in_executor(
                sentry_sdk.capture_exception, e)
        finally:
            session.close()
        return ws

    async def json_handler(self, request):
        return await self.handler(request, json_format=True)


def setup_routes(app):
    websock_handler = WebsocketHandler()
    app.add_routes([
        web.get(settings.WEBSOCKET_URL, websock_handler.handler),
        web.get(settings.WEBSOCKET_URL_NEW, websock_handler.json_handler),
    ])
