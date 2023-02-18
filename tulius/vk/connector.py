import json
import logging
import urllib.parse

from django.conf import settings
import requests


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
        url += urllib.parse.urlencode(kwargs)
        if kwargs and access_token:
            url += '&'
        if access_token:
            url += urllib.parse.urlencode({'access_token': access_token})
        response = requests.request(
            http_method, url, timeout=settings.REQUESTS_TIMEOUT)
        if response.status_code in [200, 201]:
            content = json.loads(response.text)
            return content
        raise Exception(response.text)

    def request_access_key(self, code, old_reddirect):
        args = {}
        args['client_id'] = self.key
        args['client_secret'] = self.secret
        args['code'] = code
        args['redirect_uri'] = old_reddirect
        url = 'https://oauth.vk.com/access_token?' + urllib.parse.urlencode(
            args)
        response = requests.get(url, timeout=settings.REQUESTS_TIMEOUT)
        if response.status_code not in [200, 201]:
            raise Exception(response.text)
        return json.loads(response.text)

    def user_get(self, pk, fields, access_token):
        params = {'user_id': pk, 'fields': ','.join(fields), 'v': '5.28'}
        data = self.request('users.get', access_token=access_token, **params)
        if data:
            return data['response'][0]
        return None  # not sure
