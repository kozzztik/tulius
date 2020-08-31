from tulius.forum.threads import mutations
from tulius.forum.threads import models
from tulius.forum.rights import models as rights_models


@mutations.on_mutation(mutations.ThreadFixCounters)
class UpdateRights(mutations.Mutation):
    with_descendants = True

    def _rights_for_root(self, instance, rights):
        if rights['all'] is None:
            rights['all'] = models.ACCESS_OPEN
        if rights['all'] & models.ACCESS_NO_INHERIT:
            rights['all_inherit'] = models.ACCESS_OPEN
        self._process_granted_exceptions(instance, rights)
        self._process_author(instance, rights)

    @staticmethod
    def _query_granted_exceptions(instance):
        return instance.granted_rights.all()

    def _process_granted_exceptions(self, instance, rights):
        for right in self._query_granted_exceptions(instance):
            access_level = rights['all'] | right.access_level
            access_level |= rights['users'].get(right.user_id, 0)
            if access_level & models.ACCESS_MODERATE:
                access_level |= models.ACCESS_OWN
            rights['users'][right.user_id] = access_level

    @staticmethod
    def _process_author(instance, rights):
        rights['users'][instance.user.pk] = \
            rights['users'].get(instance.user.pk, 0) | models.ACCESS_OWN

    @staticmethod
    def _process_parent_rights(instance, rights, parent_rights):
        parent_all = parent_rights['all']
        if parent_all & models.ACCESS_NO_INHERIT:
            parent_all = parent_rights['all_inherit']
        if rights['all'] is None:
            rights['all'] = parent_all
        if rights['all'] & models.ACCESS_NO_INHERIT:
            rights['all_inherit'] = parent_all
        # process parent exceptions
        for user_id, right in parent_rights['users'].items():
            if (not right & models.ACCESS_MODERATE) and \
                    instance.default_rights is not None:
                right &= instance.default_rights
            if right:
                rights['users'][int(user_id)] = \
                    rights['users'].get(int(user_id), 0) | right

    def process_thread(self, instance):
        instance.data['rights'] = rights = {
            'all': instance.default_rights,
            'users': {}}
        if not instance.parent_id:
            self._rights_for_root(instance, rights)
            return
        parent_rights = instance.parent.data['rights']
        self._process_parent_rights(instance, rights, parent_rights)
        self._process_granted_exceptions(instance, rights)
        self._process_author(instance, rights)


class UpdateRightsOnThreadCreate(UpdateRights):
    with_descendants = False
    data = None

    def __init__(self, thread, data, **kwargs):
        super(UpdateRightsOnThreadCreate, self).__init__(thread, **kwargs)
        self.data = data
        if data['default_rights'] is None:
            thread.default_rights = None
        else:
            thread.default_rights = int(data['default_rights'])

    def _query_granted_exceptions(self, instance):
        return [
            rights_models.ThreadAccessRight(
                thread=instance, user_id=int(right['user']['id']),
                access_level=right['access_level'])
            for right in self.data['granted_rights']]

    def save_exceptions(self):
        for right in self._query_granted_exceptions(self.thread):
            right.save()
