from django import urls
from django.core import exceptions
from django.utils import html

from tulius.forum import signals
from tulius.forum.threads import api
from tulius.gameforum import base
from tulius.gameforum import consts
from tulius.gameforum import rights
from djfw.wysibb.templatetags import bbcodes


class BaseThreadAPI(api.BaseThreadView, base.VariationMixin):
    plugin_id = consts.GAME_FORUM_SITE_ID

    def _get_rights_checker(self, thread, parent_rights=None):
        return rights.RightsChecker(
            self.variation, thread, self.user, parent_rights=parent_rights)

    def role_to_json(self, role_id, detailed=False):
        if role_id is None:
            return {
                'id': None,
                'title': 'Ведущий',
                'url': None,
                'sex': None,
                'avatar': None,
                'online_status': None,
                'trust': None,
                'show_trust_marks': False,
            }
        role = self.rights.all_roles[role_id]
        data = {
            'id': role.id,
            'title': html.escape(role.name),
            'url': role.get_absolute_url(),
        }
        if detailed:
            on = role.is_online() if role.show_in_online_character else None
            data.update({
                'sex': role.sex,
                'avatar': role.avatar.image.url if (
                    role.avatar and role.avatar.image) else '',
                'online_status': on,
                'owned': (
                    self.user.is_authenticated and
                    (role.user_id == self.user.id)),
                'trust': role.trust_value if role.show_trust_marks else None,
                'show_trust_marks': role.show_trust_marks,
            })
        return data

    def thread_url(self, thread_id):
        return urls.reverse(
            'game_forum_api:thread',
            kwargs={
                'variation_id': self.variation.id, 'pk': thread_id})

    def room_to_json(self, thread):
        data = {
            'id': thread.pk,
            'title': html.escape(thread.title),
            'body': bbcodes.bbcode(thread.body),
            'room': thread.room,
            'deleted': thread.deleted,
            'important': thread.important,
            'closed': thread.closed,
            'user': self.role_to_json(thread.data1),
            'moderators': [
                self.role_to_json(user) for user in thread.moderators],
            'accessed_users': None if thread.accessed_users is None else [
                self.role_to_json(user) for user in thread.accessed_users
            ],
            'threads_count': thread.threads_count if thread.room else None,
            'comments_count': thread.comments_count,
            'pages_count': thread.pages_count,
            'url': self.thread_url(thread.pk),
        }
        signals.thread_room_to_json.send(self, thread=thread, response=data)
        return data

    def process_role(self, init_role_id, data):
        role_id = data.get('role_id')
        if role_id:
            if role_id not in self.rights.all_roles:
                raise exceptions.PermissionDenied('Role does not exist')
            if role_id == init_role_id:
                return role_id
        if role_id not in self.rights.user_write_roles:
            raise exceptions.PermissionDenied('Role is not accessible here')
        return role_id

    def create_thread(self, data):
        obj = super(BaseThreadAPI, self).create_thread(data)
        obj.data1 = self.process_role(None, data)
        return obj

    def update_thread(self, data):
        super(BaseThreadAPI, self).update_thread(data)
        self.obj.data1 = self.process_role(self.obj.data1, data)
        editor_role = data['edit_role_id']
        if editor_role not in self.rights.user_write_roles:
            raise exceptions.PermissionDenied()
        self.obj.data2 = editor_role


class ThreadAPI(api.ThreadView, BaseThreadAPI):
    def obj_to_json(self):
        data = super(ThreadAPI, self).obj_to_json()
        data['user'] = self.role_to_json(self.obj.data1, detailed=True)
        data['edit_role_id'] = self.obj.data2
        return data
