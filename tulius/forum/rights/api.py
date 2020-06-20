import json

from django import shortcuts
from django import urls
from django.core import exceptions
from django.db import transaction
from django.contrib import auth

from tulius.forum import models
from tulius.forum.threads import api


class GrantedRightsAPI(api.BaseThreadView):
    model = models.ThreadAccessRight
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

    def get_context_data(self, **kwargs):
        self.get_parent_thread(**kwargs)
        if not self.rights.edit:
            exceptions.PermissionDenied()
        objs = self.model.objects.filter(thread=self.obj).order_by('id')
        return {
            'granted_rights': [self.right_to_json(r) for r in objs]
        }

    def create_right(self, data):
        obj = self.model.objects.get_or_create(
            thread=self.obj, user_id=data['user']['id'],
            defaults={'access_level': data['access_level']}
        )[0]
        obj.access_level = obj.access_level | data['access_level']
        return obj

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
        self.obj.access_type = data['access_type']
        self.obj.save()
        return {'access_type': self.obj.access_type}

    def options(self, request, **kwargs):
        users = auth.get_user_model().objects.filter(
            is_active=True, username__istartswith=request.GET['query'])[:10]
        return {
            "users": [{"id": u.pk, "name": u.username} for u in users]
        }


class GrantedRightAPI(GrantedRightsAPI):
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

    def post(self,  *args, right_id=None, **kwargs):
        self.get_parent_thread(**kwargs)
        if not self.rights.edit:
            raise exceptions.PermissionDenied()
        data = json.loads(self.request.body)
        with transaction.atomic():
            obj = shortcuts.get_object_or_404(
                self.model.objects.select_for_update(), pk=right_id)
            obj.access_level = data['access_level']
            obj.save()
        return self.right_to_json(obj)
