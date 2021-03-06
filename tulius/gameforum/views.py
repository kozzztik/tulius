from django import http
from django import shortcuts
from django import urls
from django.views import generic
from django.core import exceptions
from django.utils import html
from django.db import transaction
from django.db.models import query_utils

from tulius.gameforum import base
from tulius.games import models as game_models
from tulius.gameforum import models as game_forum_models
from tulius.gameforum import core
from tulius.gameforum.threads import models as thread_models
from tulius.gameforum.other import trust_marks
from tulius.stories import models as stories_models


class RedirrectAPI(generic.View):
    @staticmethod
    def get(*args, **kwargs):
        pk = int(kwargs['pk'])
        thread = thread_models.Thread.objects.get(pk=pk)
        return http.JsonResponse({
            'variation_id': thread.variation_id,
            'room': thread.room,
        })


class VariationAPI(base.VariationMixin):
    obj = None

    def check_rights(self):
        if self.variation.game:
            return self.variation.game.read_right(self.user)
        return self.variation.edit_right(self.user)

    @staticmethod
    def game_to_json(game):
        return {
            'id': game.id,
            'top_banner_url': game.top_banner.url if game.top_banner else None,
            'bottom_banner_url':
                game.bottom_banner.url if game.bottom_banner else None,
        }

    def process_trust_marks(self, roles):
        marks = game_forum_models.Trustmark.objects.filter(
            variation=self.obj, user=self.user)
        for role in roles:
            role.my_trust = None
            for mark in marks:
                if mark.role_id == role.id:
                    role.my_trust = trust_marks.mark_to_percents(
                        mark.value)
                    break

    def get_context_data(self, **kwargs):
        self.obj = self.variation
        if not self.check_rights():
            raise exceptions.PermissionDenied()
        admin = (not self.obj.game) or self.obj.game.edit_right(self.user)
        all_roles = list(stories_models.Role.objects.filter(
            variation=self.obj, deleted=False))
        roles_list = []
        if self.obj.game:
            if self.obj.game.edit_right(self.user):
                roles_list = all_roles.copy()
            elif self.obj.game.status >= game_models.GAME_STATUS_FINISHING:
                roles_list = [
                    role for role in all_roles if role.show_in_character_list]
            elif self.user.is_authenticated:
                roles_list = [
                    role for role in all_roles if role.user_id == self.user.id]
        if admin:
            character_list = all_roles.copy()
        else:
            character_list = [
                r for r in all_roles
                if r.show_in_character_list or r in roles_list]

        if not self.user.is_anonymous:
            self.process_trust_marks(character_list)

        query = query_utils.Q(variation=self.obj) | query_utils.Q(
            story_id=self.obj.story_id, variation=None)
        if not admin:
            query = query & query_utils.Q(admins_only=False)
        materials = stories_models.AdditionalMaterial.objects.filter(query)
        illustrations = stories_models.Illustration.objects.filter(query)
        if (not self.variation.thread) and self.user.is_authenticated:
            with transaction.atomic():
                variation = stories_models.Variation.objects.select_for_update(
                ).get(pk=self.variation.pk)
                self.obj.thread = variation.thread = core.create_game_forum(
                    self.user, variation)
                variation.save()
        return {
            'id': self.obj.id,
            'url': urls.reverse(
                'game_forum_api:variation',
                kwargs={'variation_id': self.variation.id}),
            'game':
                self.game_to_json(self.obj.game) if self.obj.game_id else None,
            'thread_id': self.obj.thread_id,
            'write_right': (
                (not self.obj.game) or self.obj.game.write_right(self.user)),
            'characters': [{
                'id': role.id,
                'title': html.escape(role.name),
                'avatar': role.avatar.image.url if role.avatar else None,
                'comments_count': role.comments_count,
                'trust_value': role.trust_value,
                'my_trust': getattr(role, 'my_trust', None),
                'description': role.description,
            } for role in character_list],
            'roles': [{
                'id': role.id,
                'title': html.escape(role.name),
                'avatar': role.avatar.image.url if role.avatar else None,
                'comments_count': role.comments_count,
                'assigned': role.user_id == self.user.pk,
            } for role in roles_list],
            'materials': [{
                'id': m.id,
                'url': m.url(),
                'title': html.escape(m.name),
            } for m in materials],
            'illustrations': [{
                'id': m.id,
                'title': m.name,
                'url': m.image.url if m.image else None,
                'thumb': m.thumb.url if m.thumb else None,
            } for m in illustrations],
        }


class GameAPI(generic.View):
    @staticmethod
    def get(request, pk, **kwargs):
        variation = shortcuts.get_object_or_404(
            stories_models.Variation, game_id=pk)
        if not variation.game.read_right(request.user):
            raise exceptions.PermissionDenied()
        return http.JsonResponse({
            'variation_id': variation.id,
            'thread_id': variation.thread_id,
        })
