import json
import logging

from django_h2.sse import SSEResponse
from django.conf import settings
import redis
from redis import asyncio as aioredis

logger = logging.getLogger('sse')


CHANNEL_PUBLIC = 'public'
CHANNEL_USER = 'user-{}'


class RedisChannel:
    def __init__(self, user, channel_names, request):
        self.channel_names = channel_names
        self.response = SSEResponse(request, handler=self.handler())
        self.user = user

    async def handler(self):
        redis_client = aioredis.from_url(settings.REDIS_LOCATION)
        pubsub = redis_client.pubsub()
        try:
            await pubsub.subscribe(
                **{
                    f'{settings.ENV}_{name}': self._get_message
                    for name in self.channel_names
                }
            )
            await pubsub.run(
                exception_handler=self._pubsub_exc_handler, poll_timeout=30)
        finally:
            await pubsub.aclose()

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


def publish_message(channel, message):
    redis_client = redis.Redis(
        settings.REDIS_CONNECTION['host'],
        settings.REDIS_CONNECTION['port'],
        db=settings.REDIS_CONNECTION['db']
    )
    return redis_client.publish(
        f'{settings.ENV}_{channel}', json.dumps(message)
    )


def publish_message_to_user(user_id, message):
    return publish_message(CHANNEL_USER.format(user_id), message)
