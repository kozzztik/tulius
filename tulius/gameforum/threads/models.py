from django import urls
from django.db import models
from django.contrib.auth import get_user_model

from tulius.forum.threads import models as thread_models


User = get_user_model()


class RolesRights:
    data = None

    def __init__(self, instance, name, default):
        self.data = instance.data

    def __getitem__(self, item):
        for user in self.data['roles']:
            if user['id'] == item:
                return user['value']
        return self.data['roles_all']

    def __setitem__(self, key, value):
        for user in self.data['roles']:
            if user['id'] == key:
                user['value'] = value
                return
        self.data['roles'].append({'id': key, 'value': value})

    def __iter__(self):
        for i in self.data['roles']:
            yield i['id'], i['value']

    @property
    def all(self):
        return self.data['roles_all']

    @all.setter
    def all(self, value):
        self.data['roles_all'] = value

    @property
    def all_inherit(self):
        return self.data['role_all_inherit']

    @all_inherit.setter
    def all_inherit(self, value):
        self.data['role_all_inherit'] = value


class RightsCounter(thread_models.RightsCounter):
    role = thread_models.CounterField('roles', counter_class=RolesRights)

    def cleanup(self, default=None):
        super(RightsCounter, self).cleanup(default=default)
        self.data['roles'] = []
        self.data['all_roles'] = default


class Thread(thread_models.AbstractThread):
    role_id = models.IntegerField(blank=True, null=True)
    edit_role_id = models.IntegerField(blank=True, null=True)
    variation_id = models.IntegerField(blank=False, null=False)

    rights = thread_models.CounterField('rights', counter_class=RightsCounter)

    def get_absolute_url(self):
        return urls.reverse(
            'game_forum_api:thread',
            kwargs={
                'variation_id': self.variation_id, 'pk': self.pk})

    @property
    def moderators(self):
        return [
            int(pk) for pk, right in self.rights.role
            if right & thread_models.ACCESS_MODERATE]

    @property
    def accessed_users(self):
        if self.default_rights != thread_models.NO_ACCESS:
            return None
        return [
            int(pk) for pk, right in self.rights.role
            if right & thread_models.ACCESS_READ]

    def rights_to_json(self, user):
        return {
            'write': self.write_right(user),
            'moderate': self.moderate_right(user),
            'edit': self.edit_right(user),
            'move': self.moderate_right(user),
        }
