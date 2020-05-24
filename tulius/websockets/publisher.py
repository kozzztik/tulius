import redis
from django.conf import settings

from tulius.websockets import consts


def publish_message(channel, message, *params):
    redis_client = redis.Redis(
        settings.REDIS_CONNECTION['host'],
        settings.REDIS_CONNECTION['port'],
        db=settings.REDIS_CONNECTION['db']
    )
    redis_client.publish(
        consts.make_channel_name(channel),
        ' '.join([message, *(str(p) for p in params)])
    )


def publish_message_to_user(user_id, message, *params):
    publish_message(consts.CHANNEL_USER.format(user_id), message, *params)


def notify_thread_about_new_comment(thread_id, comment_id, page_id):
    publish_message(
        consts.THREAD_COMMENTS_CHANNEL.format(thread_id=thread_id),
        consts.THREAD_COMMENTS_NEW_COMMENT, comment_id, page_id)
