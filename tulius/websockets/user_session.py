import asyncio
import json
import logging
import inspect

from django.conf import settings
from django.contrib import auth
from redis import asyncio as aioredis
from asgiref.sync import sync_to_async

from tulius.forum import const as forum_const
from tulius.websockets import consts

logger = logging.getLogger('async_app')


class PubSub(aioredis.client.PubSub):
    async def run(
        self,
        *,
        exception_handler=None,
        poll_timeout: float = 1.0,
    ) -> None:
        for channel, handler in self.channels.items():
            if handler is None:
                raise aioredis.PubSubError(
                    f"Channel: '{channel}' has no handler registered")
        for pattern, handler in self.patterns.items():
            if handler is None:
                raise aioredis.PubSubError(
                    f"Pattern: '{pattern}' has no handler registered")

        await self.connect()
        while True:
            try:
                await self.get_message(
                    ignore_subscribe_messages=True, timeout=poll_timeout
                )
            except (asyncio.CancelledError, GeneratorExit):
                raise
            except BaseException as e:
                if exception_handler is None:
                    raise
                res = exception_handler(e, self)
                if inspect.isawaitable(res):
                    await res
            # Ensure that other tasks on the event loop get a chance to run
            # if we didn't have to block for I/O anywhere.
            await asyncio.sleep(0)


class UserSession:
    def __init__(self, request, ws, redis_cache, json_format):
        self.request = request
        self.ws = ws
        self.redis = None
        self.user_id = None
        self._redis_cache = redis_cache
        self.json = json_format
        self.user = None
        self.pubsub = None
        self.pubsub_task = None

    def cache_key(self, value):
        return self._redis_cache.make_key(value)

    async def auth(self):
        user = await sync_to_async(
            auth.get_user, thread_sensitive=False)(self.request)
        self.user = user
        self.user_id = self.user.pk

    @staticmethod
    def _pubsub_exc_handler(e, *args):
        logging.exception(e)

    async def subscribe_channel(self, name, func):
        logger.debug(
            'subscribe channel %s %s', self.user_id, name)
        await self.pubsub.subscribe(**{consts.make_channel_name(name): func})

    async def public_channel(self, message):
        pass

    async def user_channel(self, message):
        logger.debug('User %s message %s', self.user_id, message)
        message = json.loads(message['data'])
        direct = message.pop('.direct')
        if direct:
            if self.json:
                await self.ws.send_json(message)
            else:
                await self.ws.send_text("new_pm {}".format(message['id']))

    async def thread_comments_channel(self, message):
        logger.debug('User %s message %s', self.user_id, message)
        message = json.loads(message['data'])
        direct = message.pop('.direct')
        if direct:
            message['.namespaced'] = 'thread_comments'
            await self.ws.send_json(message)

    async def action_subscribe_comments(self, data):
        thread_id = data['id']
        async with self.redis.client() as client:
            rights = await client.get(
                self.cache_key(
                    forum_const.USER_THREAD_RIGHTS.format(
                        user_id=self.user_id, thread_id=thread_id)))
        if not rights:
            return
        await self.subscribe_channel(
            consts.THREAD_COMMENTS_CHANNEL.format(thread_id=thread_id),
            self.thread_comments_channel
        )

    async def action_unsubscribe_comments(self, data):
        logging.debug('unsubscribe %s %s', self.user_id, data['id'])
        await self.pubsub.unsubscribe(consts.make_channel_name(
            consts.THREAD_COMMENTS_CHANNEL.format(thread_id=data['id'])))

    async def action_ping(self, data):
        logger.debug('User %s message %s', self.user_id, data)
        await self.ws.send_json({
            '.direct': True,
            '.namespaced': 'session',
            '.action': 'ping',
            'data': data['data'] + '/answer',
        })

    async def process(self):
        await self.auth()
        logger.info('User %s logged in', self.user_id)
        self.redis = aioredis.from_url(settings.REDIS_LOCATION)
        self.pubsub = PubSub(self.redis.connection_pool)
        await self.subscribe_channel(
            consts.CHANNEL_PUBLIC, self.public_channel)
        self.pubsub_task = asyncio.create_task(
            self.pubsub.run(
                exception_handler=self._pubsub_exc_handler, poll_timeout=30))
        try:
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
        finally:
            logger.info('User %s closed', self.user_id)
            await self.close()

    async def close(self):
        if self.pubsub_task:
            self.pubsub_task.cancel()
            self.pubsub = None
        if self.redis:
            await self.redis.close()
