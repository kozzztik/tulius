import json

from django import dispatch
from django import shortcuts
from django.core import exceptions
from django.db import transaction
from django.contrib import auth

from tulius.forum.rights import models
from tulius.forum.threads import models as thread_models
from tulius.forum.threads import views
from tulius.forum.threads import signals as thread_signals
from tulius.forum.rights import mutations


@dispatch.receiver(thread_signals.before_create, sender=thread_models.Thread)
def before_create_thread(instance, data, preview, **_kwargs):
    if not preview:
        mutations.UpdateRightsOnThreadCreate(instance, data).apply()


@dispatch.receiver(thread_signals.after_create, sender=thread_models.Thread)
def after_create_thread(instance, data, preview, **_kwargs):
    if not preview:
        mutations.UpdateRightsOnThreadCreate(instance, data).save_exceptions()


class BaseGrantedRightsAPI(views.BaseThreadView):
    rights_model = models.ThreadAccessRight
    require_user = True

    @staticmethod
    def get_mutation(thread):
        return mutations.UpdateRights(thread)

    def create_right(self, data):
        obj = self.rights_model.objects.get_or_create(
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


class GrantedRightsAPI(BaseGrantedRightsAPI):
    def get_context_data(self, **kwargs):
        self.get_parent_thread(**kwargs)
        if not self.obj.edit_right(self.user):
            raise exceptions.PermissionDenied()
        objs = self.rights_model.objects.filter(thread=self.obj).order_by('id')
        return {
            'granted_rights': [r.to_json() for r in objs]
        }

    @transaction.atomic
    def post(self, request, **kwargs):
        self.get_parent_thread(for_update=True, **kwargs)
        if not self.obj.edit_right(self.user):
            raise exceptions.PermissionDenied()
        data = json.loads(request.body)
        obj = self.create_right(data)
        obj.save()
        self.get_mutation(self.obj).apply()
        return obj.to_json()

    @transaction.atomic
    def put(self, request, **kwargs):
        data = json.loads(request.body)
        self.get_parent_thread(for_update=True, **kwargs)
        if not self.obj.edit_right(self.user):
            raise exceptions.PermissionDenied()
        self.obj.access_type = data['access_type']
        self.get_mutation(self.obj).apply()
        return {'access_type': self.obj.access_type}

    @classmethod
    def on_fix_counters(cls, sender, thread, view, **kwargs):
        cls.get_mutation(thread).apply()


thread_signals.on_fix_counters.connect(
    GrantedRightsAPI.on_fix_counters, sender=thread_models.Thread)


class GrantedRightAPI(BaseGrantedRightsAPI):
    def get_context_data(self, **kwargs):
        self.get_parent_thread(**kwargs)
        if not self.obj.edit_right(self.user):
            raise exceptions.PermissionDenied()
        obj = self.rights_model.objects.get(pk=kwargs['right_id'])
        return obj.to_json()

    @transaction.atomic
    def delete(self, *_args, right_id=None, **kwargs):
        self.get_parent_thread(for_update=True, **kwargs)
        if not self.obj.edit_right(self.user):
            raise exceptions.PermissionDenied()
        count = self.rights_model.objects.filter(pk=right_id).delete()
        if count:
            self.get_mutation(self.obj).apply()
        return {'count': count}

    @transaction.atomic
    def post(self, request, right_id=None, **kwargs):
        self.get_parent_thread(for_update=True, **kwargs)
        if not self.obj.edit_right(self.user):
            raise exceptions.PermissionDenied()
        data = json.loads(request.body)
        obj = shortcuts.get_object_or_404(
            self.rights_model.objects.select_for_update(), pk=right_id)
        obj.access_level = data['access_level']
        obj.save()
        self.get_mutation(self.obj).apply()
        return obj.to_json()
