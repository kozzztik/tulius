from tulius.forum.threads import mutations
from tulius.forum.threads import models
from tulius.forum.rights import models as rights_models


class UpdateRights(mutations.Mutation):
    with_descendants = True

    def _rights_for_root(self, instance, rights):
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
        rights['all'] &= parent_rights['all']
        # process parent exceptions
        for user_id, right in parent_rights['users'].items():
            if not right & models.ACCESS_MODERATE:
                if instance.access_type >= models.THREAD_ACCESS_TYPE_NO_WRITE:
                    right &= ~models.ACCESS_WRITE
                if instance.access_type == models.THREAD_ACCESS_TYPE_NO_READ:
                    right &= ~models.ACCESS_READ
                right &= ~models.ACCESS_EDIT
            if right:
                rights['users'][int(user_id)] = right

    def process_thread(self, instance):
        instance.data['rights'] = rights = {
            'all': models.default_rights[
                max(instance.access_type, models.THREAD_ACCESS_TYPE_OPEN)],
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
        thread.access_type = int(data['access_type'])

    def _query_granted_exceptions(self, instance):
        return [
            rights_models.ThreadAccessRight(
                thread=instance, user_id=int(right['user']['id']),
                access_level=right['access_level'])
            for right in self.data['granted_rights']]

    def save_exceptions(self):
        for right in self._query_granted_exceptions(self.thread):
            right.save()
