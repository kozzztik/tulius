import json

from django import shortcuts
from django.core import exceptions
from django.core.cache import cache
from django.db import transaction

from tulius.core.ckeditor import html_converter
from tulius.forum import core
from tulius.forum import const
from tulius.forum.threads import models
from tulius.forum.threads import signals
from tulius.forum.threads import mutations
from tulius.forum.rights import models as rights_models


class BaseThreadView(core.BaseAPIView):
    obj = None
    thread_model = models.Thread

    def get_parent_thread(
            self, pk=None, for_update=False, deleted=False, **_kwargs):
        thread_id = int(pk)
        query = self.thread_model.objects.filter(deleted=deleted)
        if for_update:
            query = query.select_for_update()
        self.obj = shortcuts.get_object_or_404(query, id=thread_id)
        if not self.obj.read_right(self.user):
            raise exceptions.PermissionDenied()

    def create_thread(self, data):
        room = bool(data['room'])
        important = ((not room) and data.get('important', False))
        obj = self.thread_model(
            parent=self.obj, room=room,
            title=data['title'], body=data['body'],
            user=self.user,
            data={},
            important=important and self.obj.moderate_right(self.user),
        )
        obj.rights.cleanup(default=0)
        return obj

    def update_thread(self, data):
        self.obj.title = data['title']
        self.obj.body = data['body']
        if self.obj.moderate_right(self.user) and not self.obj.room:
            self.obj.important = bool(data['important'])
            self.obj.closed = bool(data['closed'])


class ThreadView(BaseThreadView):
    create_mutation = mutations.ThreadCreateMutation

    def get_context_data(self, **kwargs):
        super().get_context_data(**kwargs)
        if self.obj is None:
            self.get_parent_thread(**kwargs)
        # cache rights for async app
        cache.set(
            const.USER_THREAD_RIGHTS.format(
                user_id=self.user.id, thread_id=self.obj.pk),
            'r', const.USER_THREAD_RIGHTS_PERIOD * 60
        )
        deleted = bool(self.request.GET.get('deleted'))
        if deleted and not self.user.is_superuser:
            raise exceptions.PermissionDenied()
        return self.obj.to_json(self.user, deleted=deleted)

    @transaction.atomic
    def delete(self, request, **kwargs):
        self.get_parent_thread(for_update=True, **kwargs)
        if not self.obj.edit_right(self.user):
            raise exceptions.PermissionDenied()
        mutations.ThreadDeleteMutation(
            self.obj, self.user, request.GET['comment']).apply()
        return {'result': True}

    def put(self, request, **kwargs):
        data = json.loads(request.body)
        data['title'] = html_converter.html_to_bb(data['title'])
        data['body'] = html_converter.html_to_bb(data['body'])
        preview = data.pop('preview', False)
        transaction.set_autocommit(False)
        self.get_parent_thread(for_update=not preview, **kwargs)
        if not self.obj.write_right(self.user):
            raise exceptions.PermissionDenied()
        self.obj = self.create_thread(data)
        signals.before_create.send(
            self.thread_model, instance=self.obj, data=data, user=self.user,
            preview=preview)
        if not preview:
            self.create_mutation(self.obj, data=data, view=self).apply()
        signals.after_create.send(
            self.thread_model, instance=self.obj, data=data, preview=preview,
            user=self.user)
        transaction.commit()
        # TODO notify clients
        return self.obj.to_json(self.user)

    @transaction.atomic
    def post(self, request, **kwargs):
        data = json.loads(request.body)
        data['title'] = html_converter.html_to_bb(data['title'])
        data['body'] = html_converter.html_to_bb(data['body'])
        preview = data.pop('preview', False)
        self.get_parent_thread(for_update=True, **kwargs)
        if not self.obj.edit_right(self.user):
            raise exceptions.PermissionDenied()
        self.update_thread(data)
        signals.on_update.send(
            self.thread_model, instance=self.obj, data=data, preview=preview,
            user=self.user)
        if not preview:
            self.obj.save()
        return self.obj.to_json(self.user)


class IndexView(BaseThreadView):
    rights_model = rights_models.ThreadAccessRight
    create_mutation = mutations.ThreadCreateMutation

    def get_index(self, level):
        if level:
            threads = self.thread_model.objects.filter(
                parent__parent=None, deleted=False)
        else:
            threads = self.thread_model.objects.filter(
                parent=None, deleted=False)
        return [t for t in threads if t.read_right(self.user)]

    def get_context_data(self, **kwargs):
        all_rooms = list(self.get_index(1))
        groups = self.get_index(0)
        for group in groups:
            group.rooms = [
                thread for thread in all_rooms if thread.parent_id == group.id]
            for thread in group.rooms:
                thread.parent = group  # TODO is it needed
        response = {
            'groups': [{
                'id': group.id,
                'title': group.title,
                'rooms': [t.to_json_as_item(self.user) for t in group.rooms],
                'url': group.get_absolute_url(),
            } for group in groups]
        }
        signals.index_to_json.send(
            self.thread_model, groups=groups, user=self.user,
            response=response)
        return response

    def put(self, request, **_kwargs):
        transaction.set_autocommit(False)
        if not self.user.is_superuser:
            raise exceptions.PermissionDenied()
        data = json.loads(request.body)
        data['title'] = html_converter.html_to_bb(data['title'])
        data['body'] = html_converter.html_to_bb(data['body'])
        if not data['room']:
            raise exceptions.PermissionDenied()
        thread = self.create_thread(data)
        signals.before_create.send(
            self.thread_model, instance=thread, data=data, user=self.user,
            preview=False)
        self.create_mutation(thread, data=data, view=self).apply()
        signals.after_create.send(
            self.thread_model, instance=thread, data=data, preview=False,
            user=self.user)
        transaction.commit()
        # TODO notify clients
        return {'id': thread.pk, 'url': thread.get_absolute_url()}


class MoveThreadView(BaseThreadView):
    fix_mutation = mutations.ThreadFixCounters

    @transaction.atomic
    def put(self, request, **kwargs):
        data = json.loads(request.body)
        parent_id = data['parent_id']
        self.get_parent_thread(parent_id, for_update=True)
        if not self.obj.write_right(self.user):
            raise exceptions.PermissionDenied('No target write right')
        new_parent = self.obj
        self.get_parent_thread(for_update=True, **kwargs)
        if not self.obj.edit_right(self.user):
            raise exceptions.PermissionDenied('No source edit right')
        if self.obj.pk in new_parent.parents_ids or (
                new_parent.pk == self.obj.pk):
            raise exceptions.PermissionDenied('Cant move inside yourself')
        old_parent = self.obj.parent
        self.obj.parent = new_parent
        self.obj.parents_ids = None
        self.fix_mutation(self.obj).apply()
        if old_parent:
            obj = self.thread_model.objects.select_for_update().get(
                pk=old_parent.pk)
            self.fix_mutation(obj).apply()
        signals.after_move.send(
            self.thread_model, instance=self.obj, user=self.user,
            old_parent=old_parent)
        return self.obj.to_json(self.user)


class RestoreThreadView(BaseThreadView):
    fix_mutation = mutations.ThreadFixCounters
    restore_mutation = mutations.RestoreThread

    @transaction.atomic
    def put(self, _, **kwargs):
        if not self.user.is_superuser:
            raise exceptions.PermissionDenied()
        self.get_parent_thread(for_update=True, deleted=True, **kwargs)
        self.restore_mutation(self.obj).apply()
        self.fix_mutation(self.obj).apply()
        return self.obj.to_json(self.user)
