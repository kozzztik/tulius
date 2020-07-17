import re

from django import dispatch

from tulius.forum import signals
from tulius.forum.comments import signals as comment_signals


regexp = re.compile(r'^[\w\-_]*$')


@dispatch.receiver(signals.before_create_thread)
def before_create_thread(sender, thread, data, **kwargs):
    if thread.room:
        return
    html_data = data['media'].get('youtube')
    if html_data and regexp.match(html_data):
        thread.media['youtube'] = html_data


@dispatch.receiver(comment_signals.before_add)
def before_add_comment(sender, comment, data, view, **kwargs):
    html_data = data['media'].get('youtube')
    if (not html_data) or (not regexp.match(html_data)):
        return
    if view.obj.first_comment_id == comment.id:
        comment.media['youtube'] = view.obj.media['youtube']
    else:
        comment.media['youtube'] = html_data


@dispatch.receiver(signals.on_comment_update)
def on_comment_update(sender, comment, data, **kwargs):
    html_data = data['media'].get('youtube')
    orig_data = comment.media.get('youtube')
    if orig_data and not html_data:
        del comment.media['youtube']
    elif html_data:
        comment.media['youtube'] = html_data
    if sender.obj.first_comment_id == comment.id:
        if (not html_data) and ('youtube' in sender.obj.media):
            del sender.obj.media['youtube']
        elif html_data:
            sender.obj.media['youtube'] = html_data
