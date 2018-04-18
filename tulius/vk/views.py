import datetime
import urllib

from django import urls
from django.http.response import HttpResponseRedirect
from django.contrib.auth import authenticate, login
from django.conf import settings
from django.utils import timezone

from .connector import VKConnector
from .models import VK_Profile


def oauth_redd_url(request):
    return 'http://' + request.META['HTTP_HOST'] + urls.reverse(
        'vk:auth_success')


def vk_auth_reddirect(request):
    args = {}
    args['client_id'] = settings.VK_APP_KEY
    args['scope'] = '4194304'
    args['redirect_uri'] = oauth_redd_url(request)
    args['response_type'] = 'code'
    args['v'] = '5.28'
    args['state'] = ''
    url = 'https://oauth.vk.com/authorize?' + urllib.urlencode(args)
    return HttpResponseRedirect(url)


def vk_success_auth(request):
    code = request.GET['code']
    connector = VKConnector()
    data = connector.request_access_key(code, oauth_redd_url(request))
    pk = data['user_id']
    access_token = data['access_token']
    token_expires = int(data['expires_in'])
    email = data.get('email', None)
    try:
        profile = VK_Profile.objects.get(vk_id=pk)
    except VK_Profile.DoesNotExist:
        profile = VK_Profile(vk_id=pk)
        profile_data = connector.user_get(
            pk, ['sex', 'nickname', 'screen_name', 'photo_100'], access_token)
        profile.first_name = profile_data['first_name']
        profile.last_name = profile_data['last_name']
        profile.nickname = profile_data['nickname']
        profile.domain = profile_data['screen_name']
        profile.photo = profile_data['photo_100']
        profile.sex = int(profile_data['sex'])
    profile.access_token = access_token
    profile.token_expires = timezone.now() + datetime.timedelta(
        seconds=token_expires)
    profile.save()
    if request.user.is_anonymous:
        user = authenticate(vk_profile=profile, email=email)
        login(request, user)
        return HttpResponseRedirect('/')
    else:
        user = request.user
        user.vk_profile = profile
        user.save()
        return HttpResponseRedirect(urls.reverse('players:profile'))
