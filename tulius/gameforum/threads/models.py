from django import urls
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import html

from djfw.wysibb.templatetags import bbcodes
from tulius.forum.threads import models as thread_models
from tulius.stories import models as story_models
from tulius.forum.threads import signals


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
        super().cleanup(default=default)
        self.data['roles'] = []
        self.data['all_roles'] = default


class Thread(thread_models.AbstractThread):
    role = models.ForeignKey(
        story_models.Role, models.PROTECT,
        null=True,
        blank=True,
        related_name='threads',
    )
    edit_role = models.ForeignKey(
        story_models.Role, models.PROTECT,
        null=True,
        blank=True,
        related_name='edited_threads',
    )
    variation = models.ForeignKey(
        story_models.Variation, models.PROTECT,
        null=False,
        blank=False,
        related_name='threads',
    )

    rights = thread_models.CounterField('rights', counter_class=RightsCounter)

    def get_absolute_url(self):
        return urls.reverse(
            'game_forum_api:thread',
            kwargs={
                'variation_id': self.variation_id, 'pk': self.pk})

    @property
    def moderators(self):
        return [
            self.variation.all_roles[pk] for pk, right in self.rights.role
            if right & thread_models.ACCESS_MODERATE]

    @property
    def accessed_users(self):
        if self.default_rights != thread_models.NO_ACCESS:
            return None
        return [
            self.variation.all_roles[pk] for pk, right in self.rights.role
            if right & thread_models.ACCESS_READ]

    def rights_to_json(self, user):
        return {
            'write': self.write_right(user),
            'moderate': self.moderate_right(user),
            'edit': self.edit_right(user),
            'move': self.moderate_right(user),
        }

    def to_json_as_item(self, user):
        accessed_users = self.accessed_users
        data = {
            'id': self.pk,
            'title': html.escape(self.title),
            'body': bbcodes.bbcode(self.body),
            'room': self.room,
            'deleted': self.deleted,
            'important': self.important,
            'closed': self.closed,
            'user':
                self.variation.role_to_json(self.role_id, user),
            'moderators': [user.to_json(user) for user in self.moderators],
            'accessed_users': None if accessed_users is None else [
                user.to_json(user) for user in accessed_users
            ],
            'threads_count': self.threads_count[user],
            'rooms_count': self.rooms_count[user],
            'url': self.get_absolute_url(),
        }
        signals.to_json_as_item.send(
            self.__class__, instance=self, response=data, user=user)
        return data

    def write_roles(self, user):
        rights = self.rights.role
        result = []
        admin = self.variation.edit_right(user)
        if admin:
            result.append(None)
        for role in self.variation.all_roles.values():
            r = rights.all | rights[role.pk]
            r &= thread_models.ACCESS_WRITE
            if admin or ((role.user_id == user.pk) and r):
                result.append(role.pk)
        return result

    def rights_strict_roles(self, data, user):
        data['rights']['user_write_roles'] = self.write_roles(user)
        data['rights']['strict_read'] = None
        if not self.rights.role.all & thread_models.ACCESS_READ:
            data['rights']['strict_read'] = [
                key for key, right in self.rights.role
                if right & thread_models.ACCESS_READ]

    def to_json(self, user, deleted=False):
        data = {
            'id': self.pk,
            'title': self.title,
            'body': bbcodes.bbcode(self.body),
            'room': self.room,
            'deleted': self.deleted,
            'url': self.get_absolute_url() if self.pk else None,
            'parents': [{
                'id': parent.id,
                'title': parent.title,
                'url': parent.get_absolute_url(),
            } for parent in self.get_parents()],
            'rights': self.rights_to_json(user),
            'default_rights': self.default_rights,
        }
        children = None
        if self.room:
            children = self.get_children(
                user, deleted=deleted, variation=self.variation)
            for child in children:
                child.variation = self.variation  # for cache usage
            data['rooms'] = [
                t.to_json_as_item(user) for t in children if t.room]
            data['threads'] = [
                t.to_json_as_item(user) for t in children if not t.room]
        else:
            data['closed'] = self.closed
            data['important'] = self.important
            data['media'] = self.media
        data['user'] = self.variation.role_to_json(
            self.role_id, user, detailed=True)
        data['edit_role_id'] = self.edit_role_id
        self.rights_strict_roles(data, user)
        signals.to_json.send(
            self.__class__, instance=self, response=data, user=user,
            children=children)
        return data
