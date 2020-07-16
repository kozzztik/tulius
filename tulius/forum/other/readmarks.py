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


@dispatch.receiver(signals.after_add_comment)
def after_add_comment(sender, comment, preview, **kwargs):
    if preview or (sender.obj.first_comment_id != comment.id):
        return
    models.ThreadReadMark(
        user=sender.user, thread=sender.obj, readed_comment=comment,
        not_readed_comment=None).save()


@dispatch.receiver(signals.thread_prepare_room)
def prepare_room_list(sender, room, threads, **kwargs):
    read_marks = []
    if not sender.user.is_anonymous:
        read_marks = models.ThreadReadMark.objects.filter(
            thread__tree_id=room.tree_id,
            thread__lft__gt=room.lft,
            thread__rght__lt=room.rght,
            thread__room=False, user=sender.user)
    room.unreaded_id = None
    room.unreaded = None
    for thread in threads:
        read_mark = None
        for mark in read_marks:
            if thread.id == mark.thread_id:
                read_mark = mark
                break
        if read_mark:
            if read_mark.not_readed_comment_id:
                if (
                        (not room.unreaded_id) or
                        (read_mark.not_readed_comment_id <
                         room.unreaded_id)):
                    room.unreaded_id = read_mark.not_readed_comment_id
        else:
            if sender.user.is_anonymous:
                room.unreaded_id = False
            else:
                if thread.first_comment_id:
                    if (
                            (not room.unreaded_id) or (
                                thread.first_comment_id <
                                room.unreaded_id)):
                        room.unreaded_id = thread.first_comment_id
    if room.unreaded_id:
        room.unreaded = models.Comment.objects.select_related(
            'parent').get(id=room.unreaded_id)


@dispatch.receiver(signals.thread_prepare_threads)
def thread_prepare_thread(sender, threads, **kwargs):
    if not sender.user.is_anonymous:
        read_marks = models.ThreadReadMark.objects.filter(
            thread__parent=sender.obj, user=sender.user)
        for thread in threads:
            read_mark = None
            thread.unreaded_id = None
            thread.unreaded = None
            for mark in read_marks:
                if thread.id == mark.thread_id:
                    read_mark = mark
                    break
            if read_mark:
                thread.unreaded_id = read_mark.not_readed_comment_id
            else:
                if thread.first_comment_id:
                    thread.unreaded_id = thread.first_comment_id
            if thread.unreaded_id:
                thread.unreaded = models.Comment.objects.get(
                    id=thread.unreaded_id)
    important_threads = [thread for thread in threads if thread.important]
    if not sender.user.is_anonymous:
        unreaded_threads = [
            thread for thread in threads if (not thread.important) and
            thread.unreaded_id]
        readed_threads = [
            thread for thread in threads if (not thread.important) and (
                not thread.unreaded_id)]
    else:
        unreaded_threads = []
        readed_threads = [thread for thread in threads if (
            not thread.important)]
    del threads[:]
    threads += important_threads + unreaded_threads + readed_threads


@dispatch.receiver(signals.thread_room_to_json)
def room_to_json(sender, thread, response, **kwargs):
    if sender.user.is_anonymous:
        return
    response['unreaded'] = {
        'id': thread.unreaded.id,
        'thread': {
            'id': thread.unreaded.parent_id,
            'url': sender.thread_url(thread.unreaded.parent_id),
        },
        'page': thread.unreaded.page
    } if thread.unreaded else None


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

    def mark_room_as_read(self, room, room_rights):
        if room:
            threads = room.get_children()
        else:
            threads = models.Thread.objects.filter(
                parent=None, plugin_id=self.plugin_id)
        threads = {
            thread: self._get_rights_checker(
                thread, parent_rights=room_rights).get_rights()
            for thread in threads}
        for thread, rights in threads.items():
            if not rights.read:
                continue
            if thread.room:
                self.mark_room_as_read(thread, rights)
            else:
                self.mark_thread_as_read(thread, None)

    def mark_thread_as_read(self, thread, read_id):
        read_mark = models.ThreadReadMark.objects.filter(
            thread=thread, user=self.user).first()
        if not read_mark:
            read_mark = models.ThreadReadMark(thread=thread, user=self.user)
        if read_id:
            not_read = models.Comment.objects.filter(
                parent=thread, id__gt=read_id, deleted=False
            ).exclude(user=self.user).order_by('id').first()
        else:
            not_read = None
            read_id = thread.last_comment_id
        read_mark.readed_comment_id = read_id
        read_mark.not_readed_comment = not_read
        read_mark.save()
        return read_mark

    def post(self, *args, **kwargs):
        if 'pk' in kwargs:
            self.get_parent_thread(**kwargs)
        read_id = json.loads(self.request.body)['comment_id']
        read_mark = None
        if (not self.obj) or self.obj.room:
            self.mark_room_as_read(self.obj, self.rights)
        else:
            read_mark = self.mark_thread_as_read(self.obj, read_id)
        return {
            'last_read_id': read_id,
            'not_read_comment': not_read_comment_json(
                read_mark.not_readed_comment, self.user
            ) if read_mark and read_mark.not_readed_comment else None
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
