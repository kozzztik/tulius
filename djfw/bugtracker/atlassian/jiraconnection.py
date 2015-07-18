from djfw import httplib
import json
import logging

logger = logging.getLogger('bugtracker.jira')

class JiraConnector():
    def __init__(self, base_url, username, password, project=None, ca_certs=None, disable_certs=False):
        self.username = username
        self.password = password
        self.token = None
        self.token_name = None
        self.base_url = base_url
        self.login_info = None
        self.project = project
        self.cookies = {}
        self.ca_certs = ca_certs
        self.disable_certs = disable_certs
        
    def _get_cookies(self):
        return ';'.join("%s=%s" % (key, value) for key, value in self.cookies.items())
    
    def _request(self, uri, method="GET", data=None, absolute_url=False):
        if absolute_url:
            url = uri
        else:
            url = self.base_url + uri
        if isinstance(data, dict):
            data = json.dumps(data)
        h = httplib.Http(ca_certs=self.ca_certs, disable_ssl_certificate_validation=self.disable_certs)
        headers = {'Content-Type': 'application/json'}
        if self.cookies:
            headers['Cookie'] = self._get_cookies()
        resp, content= h.request(url, method, headers=headers, body=data)
        status = int(resp['status'])
        return status, content, resp
            
    def request(self, uri, method="GET", data=None, absolute_url=False):
        tried_to_login = False
        if not self.token:
            self.login()
            tried_to_login = True
        status, content, resp = self._request(uri, method, data, absolute_url)
        if (status in [403, 404]) and (not tried_to_login):
            self.login()
            status, content = self._request(uri, method, data, absolute_url)
        if not (status in [200, 201]):
            raise Exception('Unexpected return code ' + str(status) + ' ' + content)
        return content
    
    def request_json(self, uri, method="GET", data=None, absolute_url=False):
        content = self.request(uri, method=method, data=data, absolute_url=absolute_url)
        return json.loads(content)
    
    def login(self):
        request_data = {'username': self.username, 'password': self.password}
        status, data, resp = self._request('/rest/auth/1/session', 'POST', request_data)
        if status == 200:
            data = json.loads(data)
            session = data['session']
            self.token = session['value']
            self.token_name = session['name']
            self.login_info = data['loginInfo']
            set_cookies = resp['set-cookie'].replace(',', ' ').replace(';', ' ').split(' ')
            set_cookies = [line for line in set_cookies if line.count('=')]
            for set_cookie in set_cookies:
                set_cookie = set_cookie.split('=')
                if len(set_cookie) == 2:
                    if not set_cookie[0].lower() in ['path', 'domain', 'expires']:
                        self.cookies[set_cookie[0]] = set_cookie[1]
        elif status == 401:
            logger.critical('Cant login. Invalid login or password.')
            raise Exception('Bad login or password')
        elif status == 403:
            logger.critical('Cant login. Account is blocked.')
            raise Exception('Account is blocked')
        else:
            logger.critical('Cant login. Unknown error ' + str(status) + ' ' + data)
            raise Exception('Unknown error ' + str(status) + ' ' + data)

    def user_login_info(self):
        return self.request_json('/rest/auth/1/session')
    
    def priorities_list(self):
        return self.request_json('/rest/api/2/priority')
    
    def issue_types_list(self):
        return self.request_json('/rest/api/2/issuetype')
    
    def statuses_list(self):
        return self.request_json('/rest/api/2/status')
    
    def resolutions_list(self):
        return self.request_json('/rest/api/2/resolution')
    
    def link_types_list(self):
        return self.request_json('/rest/api/2/issueLinkType')['issueLinkTypes']
    
    def versions_list(self):
        return self.request_json('/rest/api/2/project/%s/versions?expand' % (self.project,))
    
    def components_list(self):
        return self.request_json('/rest/api/2/project/%s/components' % (self.project,))
    
    def issue_by_version(self, version_name):
        data = self.request_json('/rest/api/2/search?maxResults=10000&jql=project+%%3D+%s+AND+fixVersion+%%3D+"%s"' % (self.project, version_name,))
        return data['issues']
    
    def project_info(self, project=None):
        if not project:
            project = self.project
        return self.request_json('/rest/api/2/project/%s' % (self.project,))
    
    def post_comment(self, issue_id, comment):
        return self.request_json('/rest/api/2/issue/%s/comment' % (issue_id,), "POST", comment)
        
    def post_issue(self, issue_fields):
        issue_fields['project'] = {'key': self.project}
        return self.request_json('/rest/api/2/issue', "POST", {'fields': issue_fields})
        