from django.contrib.auth.backends import ModelBackend
from .connector import connector
import logging

class CrowdBackend(ModelBackend):
            
    def authenticate(self, username, password):
        try:
            u = connector.login(username, password)
            if not u:
                return None
            connector.update_user_permissions(u)
            local_user = connector.get_local_user(u, password)
            local_user._crowd_login = True
            local_user._crowd_user = u
            return local_user
        except E, Exception:
            logger = logging.getLogger('crowd')
            logger.error(E)
            raise
