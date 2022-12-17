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
from tulius.forum.rights import signals


@dispatch.receiver(thread_signals.after_create, sender=thread_models.Thread)
def after_create_thread(instance, data, preview, **_kwargs):
    if not preview:
        mutations.UpdateRightsOnThreadCreate(
            instance, data=data).save_exceptions()


class BaseGrantedRightsAPI(views.BaseThreadView):
    rights_model = models.ThreadAccessRight
    require_user = True
    update_mutation = mutations.UpdateRights

    def create_right(self, data):
        obj = self.rights_model.objects.get_or_create(
            thread=self.obj, user_id=data['user']['id'],
            defaults={'access_level': data['access_level']}
        )[0]
        obj.access_level = obj.access_level | data['access_level']
        return obj

    def options(self, request, *args, **kwargs):
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
        self.update_mutation(self.obj).apply()
        signals.after_update.send(
            self.thread_model, instance=self.obj, view=self)
        return obj.to_json()

    @transaction.atomic
    def put(self, request, **kwargs):
        data = json.loads(request.body)
        self.get_parent_thread(for_update=True, **kwargs)
        if not self.obj.edit_right(self.user):
            raise exceptions.PermissionDenied()
        self.obj.default_rights = data['default_rights']
        self.update_mutation(self.obj).apply()
        signals.after_update.send(
            self.thread_model, instance=self.obj, view=self)
        return {'default_rights': self.obj.default_rights}


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
            self.update_mutation(self.obj).apply()
            signals.after_update.send(
                self.thread_model, instance=self.obj, view=self)
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
        self.update_mutation(self.obj).apply()
        signals.after_update.send(
            self.thread_model, instance=self.obj, view=self)
        return obj.to_json()
