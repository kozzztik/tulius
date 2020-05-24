import json

from django import dispatch

from tulius.forum import models
from tulius.forum import signals
from tulius.forum.threads import api


def not_read_comment_json(comment, user):
    return {
        'id': comment.id,
        'page_num': comment.page,
        'count': models.Comment.objects.filter(
            parent_id=comment.parent_id, deleted=False, id__gt=comment.id
        ).exclude(user=user).count() + 1
    }


@dispatch.receiver(signals.thread_view)
def thread_view(sender, **kwargs):
    response = kwargs['response']
    last_read_id = None
    not_read_comment = None
    if sender.user.is_authenticated:
        readmark = models.ThreadReadMark.objects.filter(
            thread=sender.obj, user=sender.user).first()
        if readmark:
            last_read_id = readmark.readed_comment_id
            if readmark.not_readed_comment:
                not_read_comment = not_read_comment_json(
                    readmark.not_readed_comment, sender.user)
        elif sender.obj.first_comment_id:
            comment = models.Comment.objects.get(
                pk=sender.obj.first_comment_id)
            not_read_comment = not_read_comment_json(
                comment, sender.user)
    response['last_read_id'] = last_read_id
    response['not_read_comment'] = not_read_comment


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
        return {
            'last_read_id': read_id,
            'not_read_comment': not_read_comment_json(
                not_read, self.user) if not_read else None
        }

    def delete(self, *args, **kwargs):
        self.get_parent_thread(**kwargs)
        models.ThreadReadMark.objects.filter(
            thread=self.obj, user=self.user).delete()
        comment = None
        if self.obj.first_comment_id:
            comment = models.Comment.objects.get(pk=self.obj.first_comment_id)
        return {
            'last_read_id': None,
            'not_read_comment':
                not_read_comment_json(comment, self.user) if comment else None
        }
