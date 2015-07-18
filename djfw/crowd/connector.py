from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module
from django.utils.timezone import now
from django.conf import settings
from django.db.models import Q
from .models import User
import json
import httplib2
import logging

logger = logging.getLogger('crowd')

def create_user(crowd_user, password):
    user = crowd_user.user
    if not user: 
        try:
            from django.contrib.auth import get_user_model
            user_model = get_user_model()
        except:
            from django.contrib.auth.models import User as user_model
        users = user_model.objects.filter(Q(email=crowd_user.email)|Q(username=crowd_user.username))
        if users:
            user = users[0]
        else:
            user = user_model.objects.create_user(crowd_user.username, crowd_user.email, password)
    user.first_name = crowd_user.first_name
    user.last_name = crowd_user.last_name
    user.is_active = True
    user.is_superuser = crowd_user.is_superuser
    user.is_staff = crowd_user.is_staff
    user.save()
    return user

class NoLocalUser(Exception):
    pass

def no_create_user(crowd_user, password, is_staff, is_superuser):
    raise NoLocalUser()

def load_func(path):
    i = path.rfind('.')
    module, attr = path[:i], path[i + 1:]
    try:
        mod = import_module(module)
    except ImportError as e:
        raise ImproperlyConfigured('Error importing create user function %s: "%s"' % (path, e))
    except ValueError:
        raise ImproperlyConfigured('Error importing create user function. Is create_user a correctly defined list or tuple?')
    try:
        func = getattr(mod, attr)
    except AttributeError:
        raise ImproperlyConfigured('Module "%s" does not define a "%s" function' % (module, attr))
    return func

class CrowdConnector(object):
    def __init__(self):
        crowd_settings = getattr(settings, 'CROWD', None)
        self.crowd_settings = crowd_settings
        self.h = httplib2.Http()
        self.headers = {'content-type': 'application/json', 'accept': 'application/json'}
        self.h.add_credentials(crowd_settings['app_name'], crowd_settings['password'])
        self.super_users = crowd_settings.get('super_users', [])
        self.staff_users = crowd_settings.get('staff_users', []) + self.super_users
        self.valid_users = crowd_settings.get('valid_users', []) + self.staff_users
        self.super_groups = set(crowd_settings.get('super_groups', []))
        self.staff_groups = set(crowd_settings.get('staff_groups', [])) | self.super_groups
        self.valid_groups = set(crowd_settings.get('valid_groups', [])) | self.staff_groups
        self.check_validity = ('valid_groups' in crowd_settings) or ('valid_users' in crowd_settings)
        self.local_user = crowd_settings.get('local_user', True)
        self.crowd_cookie = crowd_settings.get('crowd_cookie', 'crowd.token_key')
        self.SSO = crowd_settings.get('SSO', False)
        
        if 'create_user' in crowd_settings:
            self.create_user = load_func(crowd_settings['create_user'])
        else:
            self.create_user = create_user if crowd_settings.get('local_user', True) else no_create_user
    
    def do_request(self, url, method, body=None,**kwargs):
        request_url = self.crowd_settings['url'] + '/usermanagement/latest/' + url
        request_body = json.dumps(body) if body else None
        try:
            resp, content = self.h.request(request_url, method, body=request_body, headers=self.headers)
        except Exception, e:
            logger.error("Failed to request url %s, %s" % (url, e))
            return None
        status = resp['status']
        if status in ['200', '201', '204']:
            return json.loads(content) if content else {}
        else:
            logger.error("Failed to request url %s. Crowd answer status %s" % (url, status))
            logger.debug(content)
            return None
        
    def user_from_response(self, data, save=True):
        username = data['name']
        try:
            u = User.objects.get(username=username)
        except User.DoesNotExist:
            u = None
        if not u:
            u = User(username=username)
        u.email = data['email']
        u.first_name = data['first-name']
        u.last_name = data['last-name']
        u.display_name = data['display-name']
        u.is_active = True
        if save:
            u.save()
        return u

    def login(self, username, password):
        content = self.do_request('authentication?username=%s' % (username,), 'POST', {'value': password})
        if not content:
            return None
        user = self.user_from_response(content)
        return user
    
    def validation_factors(self, request):
        validation_factor = {'name': 'remote_address', 'value': request.META.get('REMOTE_ADDR', '')}
        return {'validationFactors': [validation_factor]}
    
    def create_session(self, user, request):
        body = {
            'username': user.username, 
            'password': '',
            'validation-factors': self.validation_factors(request)
        }
        content = self.do_request('session?validate-password=false', 'POST', body)
        if not content:
            return None
        token = content['token']
        user = self.check_session(token)
        user.token = token
        user.save()
        return user.token
        
    def update_user_permissions(self, user):
        name = user.username
        content = self.do_request('user/group/direct?username=%s' % name, 'GET')
        if content:
            group_names = set([group['name'] for group in content['groups']])
        else:
            return None
        if self.check_validity and ((not name in self.valid_users) and (not (group_names & self.valid_groups))):
            logger.error('User access denied by settings.')
            return None
        user.is_staff = (name in self.staff_users) or (group_names & self.staff_groups)
        user.is_superuser = user.is_staff and ((name in self.super_users) or (group_names & self.super_groups))
        user.groups = ', '.join(group_names & self.valid_groups)
        user.save()
        
    def check_session(self, token, save=True):
        content = self.do_request('session/%s' % token, 'GET')
        if content:
            user = self.user_from_response(content["user"])
            user.token = token
            if save:
                user.save()
            return user
        else:
            logger.error("User login by session failed. Token %s" % token)
            return None
    
    def kill_session(self, user, request):
        if not user.token:
            return
        content = self.do_request('session/%s' % user.token, 'DELETE')
        if not content is None:
            user.token = ''
            user.save()
            request.COOKIES.pop(self.crowd_cookie)
        else:
            logger.error("Kill session failed. Token %s" % user.token)
        
    _cached_cookie_settings = None
    def get_cookie_settings(self):
        if not self._cached_cookie_settings:
            self._cached_cookie_settings = self.do_request('config/cookie', 'GET')
        return self._cached_cookie_settings
        
    def get_local_user(self, user, password):
        if user.user:
            return user.user
        else:
            try:
                local_user = self.create_user(user, password)
            except NoLocalUser:
                return user
            user.user = local_user
            user.save()
            return local_user
    
    def get_user(self, request):
        token = request.COOKIES.get(self.crowd_cookie, None)
        if not token:
            return None
        try:
            return User.objects.get(token=token)
        except User.DoesNotExist:
            return None

connector = CrowdConnector()