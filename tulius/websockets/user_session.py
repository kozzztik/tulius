import asyncio
import functools
import json
import logging

import aioredis
from django.conf import settings
from django.contrib import auth

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
        self.user = None

    def cache_key(self, value):
        return self._redis_cache.make_key(value)

    async def auth(self):
        user = await asyncio.get_event_loop().run_in_executor(
            None, functools.partial(self.threaded_auth, self.request))
        self.user = user
        self.user_id = self.user.pk

    @staticmethod
    def threaded_auth(request):
        try:
            if hasattr(asyncio, "current_task"):
                # Python 3.7 and up
                task = asyncio.current_task()
            else:
                # Python 3.6
                task = asyncio.Task.current_task()
        except RuntimeError:
            task = None
        if task is not None:
            raise Exception('That is not thread and loop safe operation!')
        return auth.get_user(request)

    async def _channel_listener_task(self, channel, name, func):
        async for message in channel.iter():
            try:
                await func(name, json.loads(message.decode('utf-8')))
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
        logger.debug('User %s message %s', self.user_id, message)
        direct = message.pop('.direct')
        if direct:
            if self.json:
                await self.ws.send_json(message)
            else:
                await self.ws.send_str("new_pm {}".format(message['id']))

    async def thread_comments_channel(self, name, message, thread_id):
        logger.debug('User %s message %s', self.user_id, message)
        direct = message.pop('.direct')
        if direct:
            message['.namespaced'] = 'thread_comments'
            await self.ws.send_json(message)

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

        while True:
            if self.json:
                data = await self.ws.receive_json()
            else:
                data = await self.ws.receive_text()
            if data is None:
                break
            if self.json:
                method = getattr(
                    self, 'action_' + data.get('action', 'empty'), None)
                if method:
                    await method(data)
            else:
                await self.ws.send_text(data + '/answer')
        logger.info('User %s closed', self.user_id)

    def close(self):
        if self.redis:
            self.redis.close()
