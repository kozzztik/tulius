from tulius.forum.threads import mutations as base_mutations
from tulius.forum.threads import models as forum_models
from tulius.forum.rights import mutations
from tulius.forum.threads import signals
from tulius.gameforum import models as rights_models
from tulius.gameforum.threads import mutations as thread_mutations
from tulius.stories import models as stories_models
from tulius.games import models as game_models


class VariationMutationMixin(base_mutations.Mutation):
    variation = None
    all_roles = None
    admins = None
    guests = None

    def __init__(self, thread, variation, **_kwargs):
        super().__init__(thread)
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
            rights[user_id] = \
                forum_models.ACCESS_OWN + forum_models.ACCESS_MODERATE
        for user_id in self.guests:
            rights[user_id] |= forum_models.ACCESS_READ
        for role in self.all_roles.values():
            if role.user_id:
                rights[role.user_id] = \
                    (rights[role.user_id] or 0) | rights.role.all

    @staticmethod
    def _query_granted_exceptions(instance):
        return instance.access_roles.all()

    def _rights_for_root(self, instance: forum_models.AbstractThread):
        instance.rights.role.all = instance.rights.all
        if not instance.rights.role.all:
            instance.rights.role.all = forum_models.ACCESS_OPEN
        if instance.rights.role.all & forum_models.ACCESS_NO_INHERIT:
            instance.rights.role.all_inherit = forum_models.ACCESS_OPEN
        instance.rights.all = 0
        self._process_variation(instance.rights)
        super()._rights_for_root(instance)

    def _process_parent_rights(
            self, instance: forum_models.AbstractThread, parent):
        instance.rights.role.all = instance.default_rights
        parent_all = parent.rights.role.all
        if parent_all & forum_models.ACCESS_NO_INHERIT:
            parent_all = parent.rights.role.all_inherit
        if instance.rights.role.all is None:
            instance.rights.role.all = parent_all
        if instance.rights.role.all & forum_models.ACCESS_NO_INHERIT:
            instance.rights.role.all_inherit = parent_all
        super()._process_parent_rights(instance, parent)
        self._process_variation(instance.rights)
        # process parent role exceptions
        for role_id, right in parent.rights.role:
            if (not right & forum_models.ACCESS_MODERATE) and \
                    instance.default_rights is not None:
                right &= instance.default_rights
            instance.rights.role[role_id] = right

    def _process_granted_exceptions\
                    (self, instance: forum_models.AbstractThread):
        for right in self._query_granted_exceptions(instance):
            access_level = instance.rights.role.all | right.access_level
            access_level |= instance.rights.role[right.role_id]
            if access_level & forum_models.ACCESS_MODERATE:
                access_level |= forum_models.ACCESS_OWN
            instance.rights.role[right.role_id] = access_level
            role = self.all_roles.get(right.role_id)
            user_id = role.user_id if role else None
            if user_id:
                instance.rights[user_id] |= access_level

    def _process_author(self, instance):
        if instance.role_id:
            instance.rights.role[instance.role_id] |= forum_models.ACCESS_OWN
            user_id = self.all_roles[instance.role_id].user_id
            if user_id:
                instance.rights[user_id] |= forum_models.ACCESS_OWN
        # process game specific rules that overrides all exceptions
        if self.variation.game:
            if self.variation.game.status == \
                    game_models.GAME_STATUS_COMPLETED_OPEN:
                instance.rights.all |= forum_models.ACCESS_READ
            if self.variation.game.status > game_models.GAME_STATUS_FINISHING:
                block = forum_models.ACCESS_WRITE | forum_models.ACCESS_EDIT
                instance.rights.role.all &= ~block
                instance.rights.all &= ~block
                for pk, right in instance.rights:
                    instance.rights[pk] = right & ~block
            if self.variation.game.status >= game_models.GAME_STATUS_FINISHING:
                instance.rights.role.all |= forum_models.ACCESS_READ
                for role in self.all_roles.values():
                    if role.user_id:
                        instance.rights[role.user_id] |= \
                            forum_models.ACCESS_READ


def on_fix_counters(instance, **_kwargs):
    variation = stories_models.Variation.objects.get(pk=instance.variation_id)
    return UpdateRights(instance, variation)


base_mutations.on_mutation(UpdateRights)(base_mutations.ThreadCounters)

signals.apply_mutation.connect(
    on_fix_counters, sender=thread_mutations.ThreadFixCounters)


@base_mutations.on_mutation(thread_mutations.ThreadCreateMutation)
class UpdateRightsOnThreadCreate(
        UpdateRights, mutations.UpdateRightsOnThreadCreate,
        VariationMutationMixin):
    def __init__(
            self, thread, parent=None, data=None, variation=None, **kwargs):
        super().__init__(
            thread, parent=parent, data=data,
            variation=variation or parent.variation, **kwargs)

    def _query_granted_exceptions(self, instance):
        return [
            rights_models.GameThreadRight(
                thread=instance,
                role=self.all_roles[right['user']['id']],
                access_level=right['access_level'])
            for right in self.data['granted_rights']]
