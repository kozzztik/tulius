import json

import redis
from django.conf import settings

from tulius.websockets import consts


def publish_message(channel, message):
    redis_client = redis.Redis(
        settings.REDIS_CONNECTION['host'],
        settings.REDIS_CONNECTION['port'],
        db=settings.REDIS_CONNECTION['db']
    )
    redis_client.publish(
        consts.make_channel_name(channel), json.dumps(message)
    )


def publish_message_to_user(user, action, pk):
    publish_message(
        consts.CHANNEL_USER.format(user.id), {
            '.direct': True,
            '.action': 'new_pm',
            'id': pk,
        })


def notify_user_about_fixes(user, data):
    publish_message(
        consts.CHANNEL_USER.format(user.id), {
            '.direct': True,
            '.action': 'fixes_update',
            'data': data,
        })

def notify_thread_about_new_comment(sender, thread, comment):
    publish_message(
        consts.THREAD_COMMENTS_CHANNEL.format(thread_id=thread.id),
        {
            '.direct': True,
            '.action': 'new_comment',
            'id': comment.id,
            'parent_id': thread.id,
            'url': sender.comment_url(comment),
            'page': comment.page,
        })
