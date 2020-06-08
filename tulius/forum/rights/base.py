class RightsDescriptor:
    read = False
    view = False
    write = False
    edit = False
    move = False
    moderate = False
    limited_read = None
    # TODO refactor limited read to unify with game strict roles and get rid
    # TODO of accessed users&moderators as separate func

    def to_json(self):
        return {
            'write': self.write,
            'moderate': self.moderate,
            'edit': self.edit,
            'move': self.move,
        }


class BaseThreadRightsChecker:
    thread = None
    user = None
    _rights: RightsDescriptor = None
    _parent_rights: RightsDescriptor = None

    def __init__(self, thread, user, parent_rights=None):
        self.thread = thread
        self.user = user
        self._parent_rights = parent_rights

    def _get_rights(self) -> RightsDescriptor:
        raise NotImplementedError()

    def get_rights(self) -> RightsDescriptor:
        if not self._rights:
            self._rights = self._get_rights()
        return self._rights

    def read_right(self) -> bool:
        if not self._rights:
            self._rights = self._get_rights()
        return self._rights.read

    def _create_checker(self, thread):
        return self.__class__(thread, self.user)

    def get_parent_rights(self) -> RightsDescriptor:
        if not self._parent_rights:
            self._parent_rights = self._create_checker(
                self.thread.parent).get_rights()
        return self._parent_rights

    def _get_free_descendants(self):
        raise NotImplementedError()

    def _get_readable_protected_descendants(self):
        raise NotImplementedError()

    def get_readable_descendants(self) -> list:
        return list(self._get_free_descendants()) + list(
            self._get_readable_protected_descendants())
