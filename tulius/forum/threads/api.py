import json

from django import http
from django import shortcuts
from django import urls
from django.core import exceptions
from django.core.cache import cache
from django.utils import html
from django.db import transaction
from django.db.models import query_utils

from tulius.core.ckeditor import html_converter
from tulius.forum import plugins
from tulius.forum import const
from tulius.forum import models
from tulius.forum import signals
from tulius.forum import rights as forum_rights
from tulius.forum import online_status as online_status_plugin
from djfw.wysibb.templatetags import bbcodes


def user_to_json(user, detailed=False):
    data = {
        'id': user.id,
        'title': html.escape(str(user)),  # TODO
        'url': user.get_absolute_url(),
    }
    if detailed:
        if user.show_online_status:
            online_status = online_status_plugin.get_user_status(user.id)
        else:
            online_status = False
        data.update({
            'sex': user.sex,
            'avatar': user.avatar.url if user.avatar else '',
            'full_stars': user.full_stars(),
            'rank': html.escape(user.rank),
            'stories_author': user.stories_author(),  # TODO optimize that!
            'signature': bbcodes.bbcode(user.signature),
            'online_status': bool(online_status)
        })
    return data


class BaseThreadView(plugins.BaseAPIView):
    obj = None
    rights = None
    plugin_id = None

    def _get_rights_checker(self, thread, parent_rights=None):
        return forum_rights.default.DefaultRightsChecker(
            thread, self.user, parent_rights=parent_rights)

    def get_parent_thread(self, pk=None, for_update=False, **kwargs):
        thread_id = int(pk)
        query = models.Thread.objects.filter(deleted=False)
        if for_update:
            query = query.select_for_update()
        self.obj = shortcuts.get_object_or_404(
            query, id=thread_id, plugin_id=self.plugin_id)
        # TODO delete all sub threads and rooms on room delete so it will be
        # TODO not needed to do parent check here
        if self.obj.check_deleted():
            raise http.Http404('Post was deleted')
        self.rights = self._get_rights_checker(self.obj).get_rights()
        if not self.rights.read:
            raise exceptions.PermissionDenied()

    def _thread_list_apply_rights(self, parent_rights, thread_list):
        for thread in thread_list:
            thread.rights_checker = self._get_rights_checker(
                thread, parent_rights=parent_rights)
            thread.rights = thread.rights_checker.get_rights()
        return [thread for thread in thread_list if thread.rights.read]

    @staticmethod
    def room_descendants(room):
        if room.rght - room.lft <= 1:
            return [], []
        readable = room.rights_checker.get_readable_descendants()
        room_list = [thread for thread in readable if thread.room]
        threads = [thread for thread in readable if not thread.room]
        new_room_list = []
        # TODO remove: looks like all this magic is needed just for case
        # TODO of filtering children of deleted rooms
        while room_list:
            tested_room = room_list.pop(0)
            parent_id = tested_room.parent_id
            found_parent = (parent_id == room.id)
            if not found_parent:
                for tmp in room_list:
                    if tmp.id == parent_id:
                        found_parent = True
                        break
            if not found_parent:
                for tmp in new_room_list:
                    if tmp.id == parent_id:
                        found_parent = True
                        break
            if not found_parent:
                lft = tested_room.lft
                rght = tested_room.rght
                room_list = [
                    tmp for tmp in room_list if
                    not ((tmp.lft > lft) and (tmp.rght < rght))]
                new_room_list = [
                    tmp for tmp in new_room_list if
                    not ((tmp.lft > lft) and (tmp.rght < rght))]
            else:
                new_room_list += [tested_room]
        room_ids = [tmp.id for tmp in new_room_list]
        threads = [
            thread for thread in threads if
            (thread.parent_id == room.id) or (thread.parent_id in room_ids)]
        return new_room_list, threads

    def prepare_room_list(self, parent_rights, rooms):
        rooms = self._thread_list_apply_rights(parent_rights, rooms)
        for room in rooms:
            threads = self.room_descendants(room)[1]
            threads = self._thread_list_apply_rights(room.rights, threads)
            room.threads_count = len(threads)
            room.moderators, room.accessed_users = room.rights_checker\
                .get_moderators_and_accessed_users()
            signals.thread_prepare_room.send(
                self, room=room, threads=threads)
        return rooms

    def get_subthreads(self, is_room=False):
        threads = models.Thread.objects.filter(
            parent=self.obj, room=is_room).exclude(deleted=True)
        if not self.obj:
            threads = threads.filter(plugin_id=self.plugin_id)
        if is_room:
            return self.prepare_room_list(self.rights, threads)
        threads = threads.order_by('-last_comment_id')
        threads = self._thread_list_apply_rights(self.rights, threads)

        for thread in threads:
            thread.moderators, thread.accessed_users = thread.rights_checker\
                    .get_moderators_and_accessed_users()
        signals.thread_prepare_threads.send(self, threads=threads)
        return threads

    @staticmethod
    def thread_url(thread_id):
        return urls.reverse('forum_api:thread', kwargs={'pk': thread_id})

    def room_to_json(self, thread):
        data = {
            'id': thread.pk,
            'title': html.escape(thread.title),
            'body': bbcodes.bbcode(thread.body),
            'room': thread.room,
            'deleted': thread.deleted,
            'important': thread.important,
            'closed': thread.closed,
            'user': user_to_json(thread.user),
            'moderators': [user_to_json(user) for user in thread.moderators],
            'accessed_users': None if thread.accessed_users is None else [
                user_to_json(user) for user in thread.accessed_users
            ],
            'threads_count': thread.threads_count if thread.room else None,
            'comments_count': thread.comments_count,
            'pages_count': thread.pages_count,
            'url': self.thread_url(thread.pk),
        }
        signals.thread_room_to_json.send(self, thread=thread, response=data)
        return data

    def create_thread(self, data):
        room = bool(data['room'])
        important = ((not room) and data.get('important', False))
        return models.Thread(
            parent=self.obj, room=room,
            title=html_converter.html_to_bb(data['title']),
            body=html_converter.html_to_bb(data['body']),
            user=self.user, plugin_id=self.plugin_id,
            important=self.rights.moderate and important,
        )

    def update_thread(self, data):
        self.obj.title = data['title']
        self.obj.body = html_converter.html_to_bb(data['body'])
        if self.rights.moderate:
            self.obj.important = bool(data['important'])
            self.obj.closed = bool(data['closed'])

    def obj_to_json(self):
        data = {
            'id': self.obj.pk,
            'tree_id': self.obj.tree_id,
            'title': self.obj.title,
            'body': bbcodes.bbcode(self.obj.body),
            'room': self.obj.room,
            'deleted': self.obj.deleted,
            'url': self.thread_url(self.obj.pk) if self.obj.pk else None,
            'parents': [{
                'id': parent.id,
                'title': parent.title,
                'url': self.thread_url(parent.pk),
            } for parent in self.obj.get_ancestors()] if self.obj.pk else None,
            'rights': self.rights.to_json(),
            'access_type': self.obj.access_type,
            'first_comment_id': self.obj.first_comment_id,
        }
        if self.obj.room:
            data['rooms'] = [
                self.room_to_json(t) for t in self.get_subthreads(True)]
            data['threads'] = [
                self.room_to_json(t) for t in self.get_subthreads(False)]
        else:
            data['closed'] = self.obj.closed
            data['important'] = self.obj.important
            data['user'] = user_to_json(self.obj.user, detailed=True)
            data['media'] = self.obj.media
        return data


class ThreadView(BaseThreadView):
    def get_context_data(self, **kwargs):
        super(ThreadView, self).get_context_data(**kwargs)
        if self.obj is None:
            self.get_parent_thread(**kwargs)
        # cache rights for async app
        cache.set(
            const.USER_THREAD_RIGHTS.format(
                user_id=self.user.id, thread_id=self.obj.id),
            'r', const.USER_THREAD_RIGHTS_PERIOD * 60
        )
        response = self.obj_to_json()
        signals.thread_view.send(self, response=response)
        return response

    @transaction.atomic
    def delete(self, request, **kwargs):
        self.get_parent_thread(for_update=True, **kwargs)
        if not self.rights.edit:
            raise exceptions.PermissionDenied()
        self.obj.deleted = True
        delete_mark = models.ThreadDeleteMark(
            thread=self.obj,
            user=self.user,
            description=request.GET['comment'])
        self.obj.save()
        delete_mark.save()
        return {'result': True}

    def put(self, request, **kwargs):
        data = json.loads(request.body)
        preview = data.pop('preview', False)
        transaction.set_autocommit(False)
        self.get_parent_thread(for_update=not preview, **kwargs)
        if not self.rights.write:
            raise exceptions.PermissionDenied()
        self.obj = self.create_thread(data)
        signals.before_create_thread.send(self, thread=self.obj, data=data)
        if not preview:
            self.obj.save()
        signals.after_create_thread.send(
            self, thread=self.obj, data=data, preview=preview)
        transaction.commit()
        # TODO notify clients
        return self.obj_to_json()

    @transaction.atomic
    def post(self, request, **kwargs):
        data = json.loads(request.body)
        preview = data.pop('preview', False)
        self.get_parent_thread(for_update=True, **kwargs)
        if not self.rights.edit:
            raise exceptions.PermissionDenied()
        self.update_thread(data)
        signals.update_thread.send(
            self, thread=self.obj, data=data, preview=preview)
        if not preview:
            self.obj.save()
        return self.obj_to_json()


class IndexView(BaseThreadView):
    def get_index(self, level):
        children = list(self.get_free_index(level)) + \
            list(self.get_readable_protected_index(level))
        children = [thread for thread in children if thread.room]
        return sorted(children, key=lambda x: x.id)

    def get_readable_protected_index(self, level):
        if self.user.is_superuser:
            return models.Thread.objects.filter(
                access_type=models.THREAD_ACCESS_TYPE_NO_READ,
                plugin_id=self.plugin_id, level=level, deleted=False)
        if self.user.is_anonymous:
            return []
        query = query_utils.Q(
            thread__level=level,
            thread__access_type=models.THREAD_ACCESS_TYPE_NO_READ,
            thread__plugin_id=self.plugin_id,
            access_level__gte=models.THREAD_ACCESS_READ,
            user=self.user, thread__deleted=False)
        rights = models.ThreadAccessRight.objects.filter(query)
        rights = rights.select_related('thread')
        return [right.thread for right in rights]

    def get_free_index(self, level):
        threads = models.Thread.objects.filter(
            access_type__lt=models.THREAD_ACCESS_TYPE_NO_READ,
            plugin_id=self.plugin_id, level=level, deleted=False)
        if self.user.is_anonymous:
            return threads
        return threads.filter(query_utils.Q(
            access_type__lt=models.THREAD_ACCESS_TYPE_NO_READ
        ) | query_utils.Q(user=self.user))  # TODO: move it to protected #97

    def room_group_unreaded_url(self, rooms):
        unreaded = None
        for room in rooms:
            if room.unreaded:
                if (not unreaded) or (room.unreaded_id < unreaded.id):
                    unreaded = room.unreaded
        return self.thread_url(unreaded.pk) if unreaded else None

    def get_context_data(self, **kwargs):
        all_rooms = [thread for thread in self.get_index(1)]
        groups = self.get_index(0)
        self.rights = self._get_rights_checker(None).get_rights_for_root()
        for group in groups:
            group.rooms = [
                thread for thread in all_rooms if thread.parent_id == group.id]
            for thread in group.rooms:
                thread.parent = group
            group.rooms = self.prepare_room_list(self.rights, group.rooms)
            # TODO refactor unread url, move it to readmarks
        return {
            'groups': [{
                'id': group.id,
                'title': group.title,
                'rooms': [self.room_to_json(thread) for thread in group.rooms],
                'url': self.thread_url(group.id),
                'unreaded_url': self.room_group_unreaded_url(group.rooms),
            } for group in groups]
        }

    def put(self, request, **kwargs):
        transaction.set_autocommit(False)
        self.rights = self._get_rights_checker(None).get_rights_for_root()
        if not self.rights.moderate:
            raise exceptions.PermissionDenied()
        data = json.loads(request.body)
        if not data['room']:
            raise exceptions.PermissionDenied()
        thread = self.create_thread(data)
        signals.before_create_thread.send(self, thread=thread, data=data)
        thread.save()
        signals.after_create_thread.send(
            self, thread=thread, data=data, preview=False)
        transaction.commit()
        # TODO notify clients
        return {'id': thread.id, 'url': self.thread_url(thread.id)}


class MoveThreadView(BaseThreadView):
    @staticmethod
    def repair_thread_counters(obj, only_stats=True):
        # TODO refactor
        obj.site().core.content['Thread_rebuild'](obj, only_stats=only_stats)

    @transaction.atomic
    def put(self, request, **kwargs):
        data = json.loads(request.body)
        parent_id = data['parent_id']
        self.get_parent_thread(parent_id, for_update=True)
        if not self.rights.edit:
            raise exceptions.PermissionDenied('No target write right')
        new_parent = self.obj
        self.get_parent_thread(for_update=True, **kwargs)
        if not self.rights.edit:
            raise exceptions.PermissionDenied('No source edit right')
        if new_parent.is_descendant_of(self.obj, include_self=True):
            raise exceptions.PermissionDenied('Cant move inside yourself')
        if new_parent.plugin_id != self.obj.plugin_id:
            raise exceptions.PermissionDenied('Cant move between plugins')
        old_parent = self.obj.parent
        self.obj.parent = new_parent
        self.obj.save()
        if old_parent and ((not new_parent) or (
                old_parent.tree_id != new_parent.tree_id)):
            obj = models.Thread.objects.get(
                tree_id=old_parent.tree_id, parent=None)
            self.repair_thread_counters(obj, only_stats=True)
            obj.save()
        if new_parent:
            obj = models.Thread.objects.get(
                tree_id=new_parent.tree_id, parent=None)
            self.repair_thread_counters(obj, only_stats=True)
            obj.save()
        return self.obj_to_json()
