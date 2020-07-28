from tulius.forum.threads import mutations as base_mutations
from tulius.forum.threads import models as forum_models
from tulius.forum.rights import mutations
from tulius.gameforum import models as rights_models
from tulius.stories import models as stories_models
from tulius.games import models as game_models


class VariationMutationMixin(base_mutations.Mutation):
    variation = None
    all_roles = None
    admins = None
    guests = None

    def __init__(self, thread, variation):
        super(VariationMutationMixin, self).__init__(thread)
        self.variation = variation
        self.all_roles = {
            role.id: role for role in stories_models.Role.objects.filter(
                variation=self.variation)}
        if variation.game:
            self.admins = [
                a.user_id for a in game_models.GameAdmin.objects.filter(
                    game=self.variation.game)]
            self.guests = [
                g.user_id for g in game_models.GameGuest.objects.filter(
                    game=self.variation.game)]
        else:
            self.admins = [
                a.user_id for a in stories_models.StoryAdmin.objects.filter(
                    story=variation.story)]
            self.guests = []


class UpdateRights(mutations.UpdateRights, VariationMutationMixin):
    def _process_variation(self, rights):
        for user_id in self.admins:
            rights['users'][user_id] = \
                forum_models.ACCESS_OWN + forum_models.ACCESS_MODERATE
        for user_id in self.guests:
            rights['users'][user_id] = \
                rights['users'].get(user_id, 0) | forum_models.ACCESS_READ
        for role in self.all_roles.values():
            if role.user_id:
                rights['users'][role.user_id] = \
                    rights['users'].get(role.user_id, 0) | rights['role_all']

    @staticmethod
    def _query_granted_exceptions(instance):
        return instance.access_roles.all()

    def _rights_for_root(self, instance, rights):
        rights['role_all'] = rights['all']
        rights['all'] = 0
        rights['roles'] = {}
        self._process_variation(rights)
        super(UpdateRights, self)._rights_for_root(instance, rights)

    def _process_parent_rights(self, instance, rights, parent_rights):
        rights['role_all'] = forum_models.default_rights[
            max(instance.access_type, forum_models.THREAD_ACCESS_TYPE_OPEN)]
        rights['role_all'] &= parent_rights['role_all']
        rights['role_all'] |= rights['all']
        rights['roles'] = {}
        self._process_variation(rights)
        super(UpdateRights, self)._process_parent_rights(
            instance, rights, parent_rights)
        # process parent role exceptions
        for role_id, right in parent_rights['roles'].items():
            if not right & forum_models.ACCESS_MODERATE:
                if instance.access_type >= \
                        forum_models.THREAD_ACCESS_TYPE_NO_WRITE:
                    right &= ~right & forum_models.ACCESS_WRITE
                if instance.access_type == \
                        forum_models.THREAD_ACCESS_TYPE_NO_READ:
                    right &= ~forum_models.ACCESS_READ
                right &= ~right & forum_models.ACCESS_EDIT
            rights['roles'][role_id] = right

    def _process_granted_exceptions(self, instance, rights):
        for right in self._query_granted_exceptions(instance):
            access_level = rights['role_all'] | right.access_level
            access_level |= rights['roles'].get(right.role_id, 0)
            if access_level & forum_models.ACCESS_MODERATE:
                access_level |= forum_models.ACCESS_OWN
            rights['roles'][right.role_id] = access_level
            user_id = self.all_roles[right.role_id].user_id
            if user_id:
                rights['users'][user_id] = \
                    rights['users'].get(user_id, 0) | access_level

    def _process_author(self, instance, rights):
        if instance.role_id:
            rights['roles'][instance.role_id] = \
                rights['roles'].get(
                    instance.role_id, 0) | forum_models.ACCESS_OWN
            user_id = self.all_roles[instance.role_id].user_id
            if user_id:
                rights['users'][user_id] = \
                    rights['users'].get(user_id, 0) | forum_models.ACCESS_OWN
        # process game specific rules that overrides all exceptions
        if self.variation.game:
            if self.variation.game.status == \
                    game_models.GAME_STATUS_COMPLETED_OPEN:
                rights['all'] |= forum_models.ACCESS_READ
            if self.variation.game.status > game_models.GAME_STATUS_FINISHING:
                block = forum_models.ACCESS_WRITE | forum_models.ACCESS_EDIT
                rights['role_all'] &= ~block
                rights['all'] &= ~block
                rights['users'] = {
                    pk: right & ~block
                    for pk, right in rights['users'].items()}
            if self.variation.game.status >= game_models.GAME_STATUS_FINISHING:
                rights['role_all'] |= forum_models.ACCESS_READ
                for role in self.all_roles.values():
                    if role.user_id:
                        rights['users'][role.user_id] = rights['users'].get(
                            role.user_id, 0) | forum_models.ACCESS_READ


class UpdateRightsOnThreadCreate(
        UpdateRights, mutations.UpdateRightsOnThreadCreate,
        VariationMutationMixin):
    def _query_granted_exceptions(self, instance):
        return [
            rights_models.GameThreadRight(
                thread=instance,
                role=self.all_roles[right['user']['id']],
                access_level=right['access_level'])
            for right in self.data['granted_rights']]
