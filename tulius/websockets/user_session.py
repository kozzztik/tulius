import asyncio
import functools
import json
import logging

import aiohttp
import aioredis
from django.conf import settings
from django.contrib import auth
from django.contrib.sessions.backends import cached_db

from tulius.forum import const as forum_const
from tulius.websockets import consts

logger = logging.getLogger('async_app')


class UserSession:
    def __init__(self, request, ws, redis_cache, json_format):
        self.request = request
        self.ws = ws
        self.redis = None
        self.user_id = None
        self._redis_cache = redis_cache
        self.json = json_format

    def cache_key(self, value):
        return self._redis_cache.make_key(value)

    async def auth(self):
        session_id = self.request.cookies.get(settings.SESSION_COOKIE_NAME)
        if session_id:
            session = await self.redis.get(
                self.cache_key(cached_db.KEY_PREFIX + session_id))
            if session:
                session = self._redis_cache.get_value(session)
            if session:
                self.user_id = session.get(auth.SESSION_KEY)
                # TODO here validation is needed

    async def _channel_listener_task(self, channel, name, func):
        async for message in channel.iter():
            try:
                await func(name, message.decode('utf-8'))
            except asyncio.CancelledError:
                return
            except Exception as e:
                logger.error(e)

    async def subscribe_channel(self, name, func):
        logger.debug(
            'subscribe channel %s %s', self.user_id, name)
        channels = await self.redis.subscribe(consts.make_channel_name(name))
        for channel in channels:
            asyncio.get_event_loop().create_task(
                self._channel_listener_task(channel, name, func))

    async def public_channel(self, name, message):
        pass

    async def user_channel(self, name, message):
        kind = message.split(' ', 1)[0]
        logger.debug('User %s message %s', self.user_id, message)
        if kind in [consts.USER_NEW_PM, consts.USER_NEW_GAME_INVITATION]:
            if self.json:
                await self.ws.send_json({
                    '.namespaced': 'pm',
                    '.action': 'new_pm'
                })
            else:
                await self.ws.send_str(message)

    async def thread_comments_channel(self, name, message, thread_id):
        kind, payload = message.split(' ', 1)
        logger.debug('User %s message %s', self.user_id, message)
        if kind == consts.THREAD_COMMENTS_NEW_COMMENT:
            comment_id, page_num = payload.split(' ', 1)
            await self.ws.send_json({
                '.namespaced': 'thread_comments',
                '.action': 'new_comment',
                'thread_id': thread_id,
                'comment_id': int(comment_id),
                'page': page_num,
            })

    async def action_subscribe_comments(self, data):
        thread_id = data['id']
        rights = await self.redis.get(
            self.cache_key(
                forum_const.USER_THREAD_RIGHTS.format(
                    user_id=self.user_id, thread_id=thread_id)))
        if not rights:
            return
        await self.subscribe_channel(
            consts.THREAD_COMMENTS_CHANNEL.format(thread_id=thread_id),
            functools.partial(
                self.thread_comments_channel, thread_id=thread_id)
        )

    async def action_unsubscribe_comments(self, data):
        logging.debug('unsubscribe %s %s', self.user_id, data['id'])
        await self.redis.unsubscribe(consts.make_channel_name(
            consts.THREAD_COMMENTS_CHANNEL.format(thread_id=data['id'])))

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
                elif msg.data.startswith('{'):
                    data = json.loads(msg.data)
                    method = getattr(
                        self, 'action_' + data.get('action', 'empty'), None)
                    if method:
                        await method(data)
                else:
                    await self.ws.send_str(msg.data + '/answer')
            elif msg.type == aiohttp.WSMsgType.ERROR:
                logger.exception(
                    'ws connection closed with exception %s',
                    self.ws.exception())
        logger.info('User %s closed', self.user_id)

    def close(self):
        if self.redis:
            self.redis.close()
