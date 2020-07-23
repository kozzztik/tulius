import json

from django import dispatch

from tulius.forum import models
from tulius.forum.comments import signals as comment_signals
from tulius.forum.threads import signals as thread_signals
from tulius.forum.threads import views


@dispatch.receiver(thread_signals.room_to_json)
def room_to_json(instance, response, view, **_kwargs):
    if view.user.is_anonymous:
        return
    response['unreaded'] = {
        'id': instance.unreaded.id,
        'thread': {
            'id': instance.unreaded.parent_id,
            'url': view.thread_url(instance.unreaded.parent_id),
        },
        'page': instance.unreaded.page
    } if instance.unreaded else None


class ReadmarkAPI(views.BaseThreadView):
    require_user = True
    read_mark_model = models.ThreadReadMark
    comment_model = models.Comment

    def mark_room_as_read(self, room, room_rights):
        if room:
            threads = room.get_children()
        else:
            threads = self.thread_model.objects.filter(
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

    @classmethod
    def not_read_comment_json(cls, comment, user):
        return {
            'id': comment.id,
            'page_num': comment.page,
            'count': cls.comment_model.objects.filter(
                parent_id=comment.parent_id, deleted=False, id__gt=comment.id
            ).exclude(user=user).count() + 1
        }

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
            'not_read_comment': self.not_read_comment_json(
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
                self.not_read_comment_json(
                    comment, self.user) if comment else None
        }

    @classmethod
    def on_delete_comment(cls, sender, comment, view, **_kwargs):
        thread = view.obj
        if (comment.pk != thread.first_comment_id) and (
                thread.last_comment_id <= comment.pk):
            comments = sender.objects.filter(
                parent=thread, deleted=False, id__gt=comment.id).order_by('id')
            new_not_read = comments[0].id if comments else None
            cls.read_mark_model.objects.filter(
                thread=thread, not_readed_comment=comment.pk
            ).update(not_readed_comment=new_not_read)

    @classmethod
    def after_add_comment(cls, comment, preview, view, **_kwargs):
        if preview:
            return
        if view.obj.first_comment_id != comment.id:
            cls.read_mark_model.objects.filter(
                thread=view.obj, not_readed_comment=None
            ).exclude(user=view.user).update(not_readed_comment=comment)
        else:
            cls.read_mark_model(
                user=view.user, thread=view.obj, readed_comment=comment,
                not_readed_comment=None).save()

    @classmethod
    def on_prepare_room_list(cls, room, threads, view, **_kwargs):
        read_marks = []
        if not view.user.is_anonymous:
            read_marks = cls.read_mark_model.objects.filter(
                thread__tree_id=room.tree_id,
                thread__lft__gt=room.lft,
                thread__rght__lt=room.rght,
                thread__room=False, user=view.user)
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
                if view.user.is_anonymous:
                    room.unreaded_id = False
                else:
                    if thread.first_comment_id:
                        if (
                                (not room.unreaded_id) or (
                                    thread.first_comment_id <
                                    room.unreaded_id)):
                            room.unreaded_id = thread.first_comment_id
        if room.unreaded_id:
            room.unreaded = cls.comment_model.objects.select_related(
                'parent').get(id=room.unreaded_id)

    @classmethod
    def on_thread_prepare_thread(cls, threads, view, **_kwargs):
        if not view.user.is_anonymous:
            read_marks = cls.read_mark_model.objects.filter(
                thread__parent=view.obj, user=view.user)
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
                    thread.unreaded = cls.comment_model.objects.get(
                        id=thread.unreaded_id)
        important_threads = [thread for thread in threads if thread.important]
        if not view.user.is_anonymous:
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

    @classmethod
    def on_thread_to_json(cls, instance, view, response, **_kwargs):
        last_read_id = None
        not_read_comment = None
        if view.user.is_authenticated:
            readmark = cls.read_mark_model.objects.filter(
                thread=instance, user=view.user).first()
            if readmark:
                last_read_id = readmark.readed_comment_id
                if readmark.not_readed_comment:
                    not_read_comment = cls.not_read_comment_json(
                        readmark.not_readed_comment, view.user)
            elif instance.first_comment_id:
                comment = cls.comment_model.objects.get(
                    pk=instance.first_comment_id)
                not_read_comment = cls.not_read_comment_json(
                    comment, view.user)
        response['last_read_id'] = last_read_id
        response['not_read_comment'] = not_read_comment


@dispatch.receiver(comment_signals.on_delete)
def tmp_on_comment_delete_plugin_filter(sender, comment, view, **kwargs):
    # TODO this func will be removed with plugin_id field cleanup
    # it will use signals "sender" field
    if comment.plugin_id:
        return None
    return ReadmarkAPI.on_delete_comment(sender, comment, view, **kwargs)


@dispatch.receiver(comment_signals.after_add)
def tmp_on_after_add_comment_plugin_filter(comment, preview, view, **kwargs):
    # TODO this func will be removed with plugin_id field cleanup
    # it will use signals "sender" field
    if comment.plugin_id:
        return None
    return ReadmarkAPI.after_add_comment(comment, preview, view, **kwargs)


@dispatch.receiver(thread_signals.prepare_room)
def tmp_on_prepare_room_plugin_filter(room, threads, view, **_kwargs):
    # TODO this func will be removed with plugin_id field cleanup
    # it will use signals "sender" field
    if room.plugin_id:
        return None
    return ReadmarkAPI.on_prepare_room_list(room, threads, view, **_kwargs)


@dispatch.receiver(thread_signals.prepare_threads)
def tmp_on_prepare_threads_plugin_filter(threads, view, **kwargs):
    # TODO this func will be removed with plugin_id field cleanup
    # it will use signals "sender" field
    if view.plugin_id:
        return None
    return ReadmarkAPI.on_thread_prepare_thread(threads, view, **kwargs)


@dispatch.receiver(thread_signals.to_json)
def tmp_on_thread_to_json_plugin_filter(instance, view, response, **kwargs):
    # TODO this func will be removed with plugin_id field cleanup
    # it will use signals "sender" field
    if instance.plugin_id:
        return None
    return ReadmarkAPI.on_thread_to_json(instance, view, response, **kwargs)
