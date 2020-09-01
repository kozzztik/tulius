import re

from django import dispatch

from tulius.forum.threads import signals as thread_signals
from tulius.forum.comments import signals as comment_signals


regexp = re.compile(r'^[\w\-_]*$')


@dispatch.receiver(thread_signals.before_create)
def before_create_thread(instance, data, **_kwargs):
    if instance.room:
        return
    html_data = data['media'].get('youtube')
    if html_data and regexp.match(html_data):
        instance.media['youtube'] = html_data


@dispatch.receiver(comment_signals.before_add)
def before_add_comment(comment, data, view, **_kwargs):
    html_data = data['media'].get('youtube')
    if (not html_data) or (not regexp.match(html_data)):
        return
    if comment.is_thread():
        comment.media['youtube'] = view.obj.media['youtube']
    else:
        comment.media['youtube'] = html_data


@dispatch.receiver(comment_signals.on_update)
def on_comment_update(comment, data, view, **_kwargs):
    html_data = data['media'].get('youtube')
    orig_data = comment.media.get('youtube')
    if orig_data and not html_data:
        del comment.media['youtube']
    elif html_data:
        comment.media['youtube'] = html_data
    if comment.is_thread():
        if (not html_data) and ('youtube' in view.obj.media):
            del view.obj.media['youtube']
        elif html_data:
            view.obj.media['youtube'] = html_data


def init():
    pass
