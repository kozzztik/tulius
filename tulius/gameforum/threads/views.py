from django.core import exceptions

from tulius.forum.threads import views
from tulius.forum.threads import counters
from tulius.gameforum import base
from tulius.gameforum.threads import models as thread_models
from tulius.gameforum.threads import mutations


class CountersFix(counters.CountersFix):
    thread_model = thread_models.Thread
    mutation = mutations.ThreadFixCounters


class BaseThreadAPI(views.BaseThreadView, base.VariationMixin):
    thread_model = thread_models.Thread

    def get_parent_thread(
            self, pk=None, for_update=False, deleted=False, **_kwargs):
        super().get_parent_thread(
            pk=pk, for_update=for_update, deleted=deleted, **_kwargs)
        if self.obj.variation_id != self.variation.pk:
            raise exceptions.PermissionDenied('Wrong variation')
        self.obj.variation = self.variation  # for speedup role cache

    @classmethod
    def process_role(cls, thread, user, init_role_id, data):
        role_id = data.get('role_id')
        if role_id:
            if role_id not in thread.variation.all_roles:
                raise exceptions.PermissionDenied('Role does not exist')
            if role_id == init_role_id:
                return role_id
        if role_id not in thread.write_roles(user):
            raise exceptions.PermissionDenied('Role is not accessible here')
        return role_id

    def create_thread(self, data):
        obj = super().create_thread(data)
        obj.variation = self.variation
        obj.role_id = self.process_role(self.obj, self.user, None, data)
        return obj

    def update_thread(self, data):
        super().update_thread(data)
        self.obj.role_id = self.process_role(
            self.obj, self.user, self.obj.role_id, data)
        editor_role = data['edit_role_id']
        if editor_role not in self.obj.write_roles(self.user):
            raise exceptions.PermissionDenied()
        self.obj.edit_role_id = editor_role


class ThreadAPI(views.ThreadView, BaseThreadAPI):
    create_mutation = mutations.ThreadCreateMutation


class MoveThreadView(views.MoveThreadView, BaseThreadAPI):
    fix_mutation = mutations.ThreadFixCounters


class RestoreThreadView(views.RestoreThreadView, BaseThreadAPI):
    fix_mutation = mutations.ThreadFixCounters
