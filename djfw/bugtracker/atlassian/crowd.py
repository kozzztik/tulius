from django.conf import settings
from xml.dom.minidom import parseString
from django.contrib.auth.backends import ModelBackend
import httplib2
from django.utils.encoding import iri_to_uri

class CrowdBackend(ModelBackend):
    def authenticate(self, username, password):
        try:
            from django.contrib.auth import get_user_model
            user_model = get_user_model()
        except:
            from django.contrib.auth.models import User
            user_model = User
            
        crowd = getattr(settings, 'CROWD', None)
        if not crowd:
            return None
        users = user_model.objects.filter(username=username)
        if users.count() <= 0:
            user = None
        else:
            user = users[0]
        body='<?xml version="1.0" encoding="UTF-8"?><password><value><![CDATA[%s]]></value></password>' % (iri_to_uri(password),)
        h = httplib2.Http()
        h.add_credentials(crowd['app_name'], crowd['password'])
        url = crowd['url'] + ('/usermanagement/latest/authentication?username=%s' % (username,))
        resp, content = h.request(url, "POST", body=body, headers={'content-type': 'text/xml'})
        status = resp['status']
        if status == '200':
            if user:
                user.set_password(password)
            else:
                dom = parseString(content)
                node = dom.getElementsByTagName('email')
                email = node[0].firstChild.nodeValue
                node = dom.getElementsByTagName('first-name')
                first_name = node[0].firstChild.nodeValue
                node = dom.getElementsByTagName('last-name')
                last_name = node[0].firstChild.nodeValue
                user = user_model.objects.create_user(username, email, password)
                user.first_name = first_name
                user.last_name = last_name
                user.is_active = True
                if 'superuser' in crowd:
                    user.is_superuser = crowd['superuser']
                    user.is_staff = user.is_superuser
                user.save()
            return user
        else:
            return None