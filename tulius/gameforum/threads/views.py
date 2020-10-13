from django.core import exceptions

from tulius.forum.threads import views
from tulius.forum.threads import counters
from tulius.forum.threads import models as forum_models
from tulius.gameforum import base
from tulius.gameforum.threads import models as thread_models
from tulius.gameforum.threads import mutations
from tulius.stories import models as stories_models


class CountersFix(counters.CountersFix):
    thread_model = thread_models.Thread
    mutation = mutations.ThreadFixCounters


class BaseThreadAPI(views.BaseThreadView, base.VariationMixin):
    thread_model = thread_models.Thread
    all_roles = None

    def get_parent_thread(
            self, pk=None, for_update=False, deleted=False, **_kwargs):
        super().get_parent_thread(
            pk=pk, for_update=for_update, deleted=deleted, **_kwargs)
        if self.obj.variation_id != self.variation.pk:
            raise exceptions.PermissionDenied('Wrong variation')
        self.all_roles = {
            role.id: role for role in self.variation.roles.all()}

    def write_roles(self):
        rights = self.obj.rights.role
        result = []
        admin = self.variation.edit_right(self.user)
        if admin:
            result.append(None)
        for role in self.all_roles.values():
            r = self.obj.rights.role.all | rights[role.pk]
            r &= forum_models.ACCESS_WRITE
            if admin or ((role.user_id == self.user.pk) and r):
                result.append(role.pk)
        return result

    def process_role(self, init_role_id, data):
        role_id = data.get('role_id')
        if role_id:
            if role_id not in self.all_roles:
                raise exceptions.PermissionDenied('Role does not exist')
            if role_id == init_role_id:
                return role_id
        if role_id not in self.write_roles():
            raise exceptions.PermissionDenied('Role is not accessible here')
        return role_id

    def create_thread(self, data):
        obj = super().create_thread(data)
        obj.role_id = self.process_role(None, data)
        obj.variation_id = self.variation.pk
        return obj

    def update_thread(self, data):
        super().update_thread(data)
        self.obj.role_id = self.process_role(self.obj.role_id, data)
        editor_role = data['edit_role_id']
        if editor_role not in self.write_roles():
            raise exceptions.PermissionDenied()
        self.obj.edit_role_id = editor_role

    def _rights_strict_roles(self, data):
        data['rights']['user_write_roles'] = self.write_roles()
        data['rights']['strict_read'] = None
        rights = self.obj.rights
        if not rights.role.all & forum_models.ACCESS_READ:
            data['rights']['strict_read'] = [
                key for key, right in rights.role
                if right & forum_models.ACCESS_READ]

    def obj_to_json(self, deleted=False):
        data = super().obj_to_json(deleted=deleted)
        data['user'] = \
            self.obj.role.to_json(self.user, detailed=True) \
            if self.obj.role else stories_models.leader_json()
        data['edit_role_id'] = self.obj.edit_role_id
        self._rights_strict_roles(data)
        return data


class ThreadAPI(views.ThreadView, BaseThreadAPI):
    create_mutation = mutations.ThreadCreateMutation


class MoveThreadView(views.MoveThreadView, BaseThreadAPI):
    fix_mutation = mutations.ThreadFixCounters


class RestoreThreadView(views.RestoreThreadView, BaseThreadAPI):
    fix_mutation = mutations.ThreadFixCounters
