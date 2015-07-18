from django.utils.functional import SimpleLazyObject
from django.contrib.auth.signals import user_logged_out, user_logged_in
from django.contrib.auth import SESSION_KEY, login, logout
from .connector import connector
from .backend import CrowdBackend

CROWD_SESSION_KEY = 'crowd_token'
CROWD_DOMAIN_KEY = 'crowd_token'

def get_crowd_user(request):
    if not hasattr(request, '_cached_crowd_user'):
        request._cached_crowd_user = connector.get_user(request)
    return request._cached_crowd_user

class CrowdSession(object):
    user = None
    token = None
    domain = None
    logout = False
    login = False
    
class SessionsAuthenticationMiddleware(object):
    def __init__(self):
        user_logged_out.connect(self.logout)
        user_logged_in.connect(self.login)
        
    def process_request(self, request):
        assert hasattr(request, 'session'), "The Django authentication middleware requires session middleware to be installed. Edit your MIDDLEWARE_CLASSES setting to insert 'django.contrib.sessions.middleware.SessionMiddleware'."
        request.crowd = CrowdSession()
        token = request.COOKIES.get(connector.crowd_cookie, None)
        session = request.session.get(CROWD_SESSION_KEY, None)
        if session and (not token):
            request.crowd.logout = True
            logout(request)
        if token:
            user_id = request.session.get(SESSION_KEY, None)
            if not user_id and connector.SSO:
                crowd_user = connector.check_session(token)
                if crowd_user:
                    connector.update_user_permissions(crowd_user)
                    user = connector.get_local_user(crowd_user, None)
                    backend = CrowdBackend()
                    user.backend = user.backend = "%s.%s" % (backend.__module__, backend.__class__.__name__)
                    login(request, user)
                else:
                    request.crowd.logout = True
        request.crowd.user = SimpleLazyObject(lambda: get_crowd_user(request))
        request.crowd.token = session
        request.crowd.domain = request.session.get(CROWD_DOMAIN_KEY, None)
        
    def process_response(self, request, response):
        if not hasattr(request, 'crowd'):
            return response
        if request.crowd.logout and connector.SSO:
            domain = request.crowd.domain
            if domain and not request.get_host().find(domain):
                domain = None
            response.delete_cookie(connector.crowd_cookie, domain=domain)
        if request.crowd.login and connector.SSO:
            token = connector.create_session(request.crowd.user, request)
            if token:
                request.session[CROWD_SESSION_KEY] = token
                cookie = connector.get_cookie_settings()
                domain = cookie['domain']
                if not request.get_host().find(domain):
                    domain = None
                request.session[CROWD_DOMAIN_KEY] = domain
                request.crowd.domain = domain
                response.set_cookie(str(cookie['name']), str(token), domain=cookie['domain'], secure=cookie['secure'])
        return response

    def logout(self, sender, **kwargs):
        request = kwargs['request']
        crowd_user = connector.get_user(request)
        if crowd_user:
            connector.kill_session(crowd_user, request)
            request.crowd.logout = True
            
    def login(self, sender, **kwargs):
        request = kwargs['request']
        user = kwargs['user']
        if hasattr(user, '_crowd_login'):
            request.crowd.login = True
            request.crowd.logout = False
            request.crowd.user = user._crowd_user
