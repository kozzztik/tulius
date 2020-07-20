import json

from django import dispatch
from django import shortcuts
from django import urls
from django.core import exceptions
from django.db import transaction
from django.contrib import auth

from tulius.forum import models
from tulius.forum import signals
from tulius.forum.threads import api
from tulius.forum.threads import signals as thread_signals
from tulius.forum.rights import consts


@dispatch.receiver(signals.before_create_thread)
def before_create_thread(sender, thread, data, **kwargs):
    thread.access_type = int(data['access_type'])
    ancestors = models.Thread.objects.get_ancestors(thread)
    if (not free_access_type(thread.access_type)) and thread.parent_id:
        if thread.room:
            ancestors.filter(
                protected_threads=consts.THREAD_NO_PR
            ).update(protected_threads=consts.THREAD_HAVE_PR_ROOMS)
            ancestors.filter(
                protected_threads=consts.THREAD_HAVE_PR_THREADS
            ).update(
                protected_threads=consts.THREAD_HAVE_PR_THREADS +
                consts.THREAD_HAVE_PR_ROOMS)
        else:
            ancestors.filter(
                protected_threads=consts.THREAD_NO_PR
            ).update(protected_threads=consts.THREAD_HAVE_PR_THREADS)
            ancestors.filter(
                protected_threads=consts.THREAD_HAVE_PR_ROOMS
            ).update(
                protected_threads=consts.THREAD_HAVE_PR_THREADS +
                consts.THREAD_HAVE_PR_ROOMS)


@dispatch.receiver(signals.after_create_thread)
def after_create_thread(sender, thread, data, preview, **kwargs):
    if sender.plugin_id or preview:
        return
    for right in data['granted_rights']:
        models.ThreadAccessRight(
            thread=thread, user_id=int(right['user']['id']),
            access_level=right['access_level']).save()


class BaseGrantedRightsAPI(api.BaseThreadView):
    model = models.ThreadAccessRight
    rights_model = models.ThreadAccessRight
    require_user = True

    def right_to_json(self, right):
        return {
            'id': right.pk,
            'user': {
                'id': right.user.pk,
                'title': right.user.username,
            },
            'access_level': right.access_level,
            'url': urls.reverse(
                'forum_api:thread_right',
                kwargs={'pk': self.obj.id, 'right_id': right.pk})
        }

    def create_right(self, data):
        obj = self.model.objects.get_or_create(
            thread=self.obj, user_id=data['user']['id'],
            defaults={'access_level': data['access_level']}
        )[0]
        obj.access_level = obj.access_level | data['access_level']
        return obj

    def options(self, request, **kwargs):
        users = auth.get_user_model().objects.filter(
            is_active=True, username__istartswith=request.GET['query'])[:10]
        return {
            "users": [{"id": u.pk, "title": u.username} for u in users]
        }


def free_access_type(access_type):
    return access_type < models.THREAD_ACCESS_TYPE_NO_READ


class GrantedRightsAPI(BaseGrantedRightsAPI):
    def get_context_data(self, **kwargs):
        self.get_parent_thread(**kwargs)
        if not self.rights.edit:
            raise exceptions.PermissionDenied()
        objs = self.model.objects.filter(thread=self.obj).order_by('id')
        return {
            'granted_rights': [self.right_to_json(r) for r in objs]
        }

    def post(self, request, **kwargs):
        self.get_parent_thread(**kwargs)
        if not self.rights.edit:
            raise exceptions.PermissionDenied()
        data = json.loads(request.body)
        obj = self.create_right(data)
        obj.save()
        return self.right_to_json(obj)

    @transaction.atomic
    def put(self, request, **kwargs):
        data = json.loads(request.body)
        self.get_parent_thread(for_update=True, **kwargs)
        if not self.rights.edit:
            raise exceptions.PermissionDenied()
        old = self.obj.access_type
        self.obj.access_type = data['access_type']
        if free_access_type(old) != free_access_type(data['access_type']):
            # TODO guess that is not enough and its needed to fix have_PR flags
            # on parents
            self.on_fix_counters(self.thread_model, self.obj, self)
        self.obj.save()
        return {'access_type': self.obj.access_type}

    @classmethod
    def on_fix_counters(cls, sender, thread, view, **kwargs):
        pr_rooms = sender.objects.get_protected_descendants(
            thread).filter(room=True)
        pr_threads = sender.objects.get_protected_descendants(
            thread).filter(room=False)
        thread.protected_threads = consts.THREAD_NO_PR
        if pr_rooms:
            thread.protected_threads += consts.THREAD_HAVE_PR_ROOMS
        if pr_threads:
            thread.protected_threads += consts.THREAD_HAVE_PR_THREADS


@dispatch.receiver(thread_signals.on_fix_counters)
def tmp_on_fix_plugin_filter(sender, thread, view, **kwargs):
    # TODO this func will be removed with plugin_id field cleanup
    # it will use signals "sender" field
    if thread.plugin_id:
        return None
    return GrantedRightsAPI.on_fix_counters(sender, thread, view, **kwargs)


class GrantedRightAPI(BaseGrantedRightsAPI):
    def get_context_data(self, **kwargs):
        self.get_parent_thread(**kwargs)
        if not self.rights.edit:
            raise exceptions.PermissionDenied()
        obj = self.model.objects.get(pk=kwargs['right_id'])
        return self.right_to_json(obj)

    def delete(self, *args, right_id=None, **kwargs):
        self.get_parent_thread(**kwargs)
        if not self.rights.edit:
            raise exceptions.PermissionDenied()
        count = self.model.objects.filter(pk=right_id).delete()
        return {'count': count}

    def post(self, request, right_id=None, **kwargs):
        self.get_parent_thread(**kwargs)
        if not self.rights.edit:
            raise exceptions.PermissionDenied()
        data = json.loads(request.body)
        with transaction.atomic():
            obj = shortcuts.get_object_or_404(
                self.model.objects.select_for_update(), pk=right_id)
            obj.access_level = data['access_level']
            obj.save()
        return self.right_to_json(obj)
