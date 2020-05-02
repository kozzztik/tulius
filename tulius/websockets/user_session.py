import asyncio
import logging

import aiohttp
import aioredis
from django.conf import settings
from django.contrib import auth
from django.contrib.sessions.backends import cached_db

from tulius.websockets import consts

logger = logging.getLogger('async_app')


class UserSession:
    def __init__(self, request, ws, redis_cache):
        self.request = request
        self.ws = ws
        self.redis = None
        self.user_id = None
        self._redis_cache = redis_cache

    async def auth(self):
        session_id = self.request.cookies.get(settings.SESSION_COOKIE_NAME)
        if session_id:
            session = await self.redis.get(self._redis_cache.make_key(
                cached_db.KEY_PREFIX + session_id))
            if session:
                session = self._redis_cache.get_value(session)
            if session:
                self.user_id = session.get(auth.SESSION_KEY)
                # TODO here validation is needed

    async def _channel_listener_task(self, channel, name, func):
        async for message in channel.iter():
            await func(name, message.decode('utf-8'))

    async def subscribe_channel(self, name, func):
        channels = await self.redis.subscribe(name)
        for channel in channels:
            asyncio.get_event_loop().create_task(
                self._channel_listener_task(channel, name, func))

    async def public_channel(self, name, message):
        pass

    async def user_channel(self, name, message):
        kind = message.split(' ', 1)[0]
        logger.debug('User %s message %s', self.user_id, message)
        if kind in [consts.USER_NEW_PM, consts.USER_NEW_GAME_INVITATION]:
            await self.ws.send_str(message)

    async def process(self):
        self.redis = await aioredis.create_redis_pool((
            settings.REDIS_CONNECTION['host'],
            settings.REDIS_CONNECTION['port'],
        ), db=settings.REDIS_CONNECTION['db'])

        await self.auth()
        logger.info('User %s logged in', self.user_id)

        await self.subscribe_channel(
            consts.CHANNEL_PUBLIC, self.public_channel)
        if self.user_id:
            await self.subscribe_channel(
                consts.CHANNEL_USER.format(self.user_id),
                self.user_channel)

        async for msg in self.ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                if msg.data == 'close':
                    await self.ws.close()
                else:
                    await self.ws.send_str(msg.data + '/answer')
            elif msg.type == aiohttp.WSMsgType.ERROR:
                logger.exception(
                    'ws connection closed with exception %s',
                    self.ws.exception())
        logger.info('User %s closed', self.user_id)
