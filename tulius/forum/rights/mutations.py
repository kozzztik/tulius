from tulius.forum.threads import mutations
from tulius.forum.threads import models
from tulius.forum.rights import models as rights_models


@mutations.on_mutation(mutations.ThreadFixCounters)
class UpdateRights(mutations.Mutation):
    with_descendants = True

    def _rights_for_root(self, instance: models.AbstractThread):
        if instance.rights.all is None:
            instance.rights.all = models.ACCESS_OPEN
        if instance.rights.all & models.ACCESS_NO_INHERIT:
            instance.rights.all_inherit = models.ACCESS_OPEN
        self._process_granted_exceptions(instance)
        self._process_author(instance)

    @staticmethod
    def _query_granted_exceptions(instance: models.AbstractThread):
        return instance.granted_rights.all()

    def _process_granted_exceptions(self, instance: models.AbstractThread):
        for right in self._query_granted_exceptions(instance):
            access_level = instance.rights.all | right.access_level
            access_level |= instance.rights[right.user_id]
            if access_level & models.ACCESS_MODERATE:
                access_level |= models.ACCESS_OWN
            instance.rights[right.user_id] = access_level

    @staticmethod
    def _process_author(instance):
        instance.rights[instance.user.pk] |= models.ACCESS_OWN

    @staticmethod
    def _process_parent_rights(instance: models.AbstractThread, parent):
        parent_all = parent.rights.all
        if parent_all & models.ACCESS_NO_INHERIT:
            parent_all = parent.rights.all_inherit
        if instance.rights.all is None:
            instance.rights.all = parent_all
        if instance.rights.all & models.ACCESS_NO_INHERIT:
            instance.rights.all_inherit = parent_all
        # process parent exceptions
        for user_id, right in parent.rights:
            if (not right & models.ACCESS_MODERATE) and \
                    instance.default_rights is not None:
                right &= instance.default_rights
            if right:
                instance.rights[user_id] |= right

    def process_thread(self, instance: models.AbstractThread):
        instance.rights.cleanup(default=instance.default_rights)
        if not instance.parent:
            self._rights_for_root(instance)
            return
        self._process_parent_rights(instance, instance.parent)
        self._process_granted_exceptions(instance)
        self._process_author(instance)


mutations.on_mutation(UpdateRights)(mutations.ThreadCounters)


@mutations.on_mutation(mutations.ThreadCreateMutation)
class UpdateRightsOnThreadCreate(UpdateRights):
    with_descendants = False
    data = None

    def __init__(self, thread, parent=None, data=None, **kwargs):
        super().__init__(thread, **kwargs)
        self.data = data or parent.data
        if self.data['default_rights'] is None:
            thread.default_rights = None
        else:
            thread.default_rights = int(self.data['default_rights'])

    def _query_granted_exceptions(self, instance):
        return [
            rights_models.ThreadAccessRight(
                thread=instance, user_id=int(right['user']['id']),
                access_level=right['access_level'])
            for right in self.data['granted_rights']]

    def save_exceptions(self):
        for right in self._query_granted_exceptions(self.thread):
            right.save()
