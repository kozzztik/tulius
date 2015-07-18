from django.conf import settings
from djfw import httplib
import json
import logging
import urllib

logger = logging.getLogger('tulius.vk')

class VKConnector():
    def __init__(self):
        self.key = settings.VK_APP_KEY
        self.secret = settings.VK_APP_SECRET
        self.base_url = 'https://api.vk.com/method/'
        
    def request(self, method, http_method="GET", access_token=None, **kwargs):
        url = self.base_url + method
        if kwargs or access_token:
            url += '?'
        url += urllib.urlencode(kwargs)
        if kwargs and access_token:
            url += '&'
        if access_token:
            url += urllib.urlencode({'access_token': access_token})
        h = httplib.Http()
        resp, content= h.request(url, http_method)
        status = int(resp['status'])
        if (status in [200, 201]):
            content = json.loads(content)
            return content
        else:
            raise Exception(content)
        
    def request_access_key(self, code, old_reddirect):
        args = {}
        args['client_id'] = self.key
        args['client_secret'] = self.secret
        args['code'] = code
        args['redirect_uri'] = old_reddirect
        url = 'https://oauth.vk.com/access_token?' + urllib.urlencode(args)
        h = httplib.Http()
        resp, content= h.request(url)
        status = int(resp['status'])
        if not (status in [200, 201]):
            raise Exception(content)
        else:
            return json.loads(content)
            
    def user_get(self, pk, fields, access_token):
        params = {'user_id': pk, 'fields': ','.join(fields), 'v': '5.28'}
        data = self.request('users.get', access_token=access_token, **params)
        if data:
            return data['response'][0]