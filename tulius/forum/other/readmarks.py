import json

from django import dispatch

from tulius.forum import models
from tulius.forum import signals
from tulius.forum.threads import api


@dispatch.receiver(signals.thread_view)
def thread_view(sender, **kwargs):
    response = kwargs['response']
    last_read_id = None
    if sender.user.is_authenticated:
        readmark = models.ThreadReadMark.objects.filter(
            thread=sender.obj, user=sender.user).first()
        if readmark:
            last_read_id = readmark.readed_comment_id
    response['last_read_id'] = last_read_id


class ReadmarkAPI(api.BaseThreadView):
    require_user = True

    def post(self, *args, **kwargs):
        thread_id = int(kwargs['pk'])
        read_id = json.loads(self.request.body)['comment_id']
        read_mark = models.ThreadReadMark.objects.filter(
            thread_id=thread_id, user=self.user).first()
        if not read_mark:
            self.get_parent_thread(**kwargs)
            read_mark = models.ThreadReadMark(thread=self.obj, user=self.user)
        not_read = models.Comment.objects.filter(
            parent_id=thread_id, id__gt=read_id, deleted=False
        ).exclude(user=self.user).order_by('id').first()
        read_mark.readed_comment_id = read_id
        read_mark.not_readed_comment = not_read
        read_mark.save()
        return {'last_read_id': read_id}

    def delete(self, *args, **kwargs):
        thread_id = int(kwargs['pk'])
        models.ThreadReadMark.objects.filter(
            thread_id=thread_id, user=self.user).delete()
        return {'last_read_id': None}
