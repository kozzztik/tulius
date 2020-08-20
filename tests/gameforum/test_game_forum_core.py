import re

from django.test import client as django_client

from tulius.forum.threads import models
from tulius.stories import models as stories_models


def test_copy_game_forum(
        variation, variation_forum, admin, detective, superuser):
    base_url = f'/api/game_forum/variation/{variation.pk}/'
    # create a thread with "no read" and no role
    response = admin.put(
        base_url + f'thread/{variation_forum.id}/', {
            'title': 'thread', 'body': 'thread description',
            'room': False, 'default_rights': models.NO_ACCESS,
            'granted_rights': [],
            'important': True, 'media': {}})
    assert response.status_code == 200
    thread1 = response.json()
    response = admin.put(
        base_url + f'thread/{variation_forum.id}/', {
            'title': 'thread', 'body': 'thread description',
            'room': False, 'default_rights': models.NO_ACCESS,
            'granted_rights': [], 'role_id': detective.pk,
            'important': False, 'media': {}})
    assert response.status_code == 200
    # grant rights to read thread by detective
    response = admin.post(
        thread1['url'] + 'granted_rights/', {
            'user': {'id': detective.pk},
            'access_level': models.ACCESS_READ
        }
    )
    assert response.status_code == 200
    # create a detective comment
    response = admin.post(
        thread1['url'] + 'comments_page/', {
            'reply_id': thread1['first_comment_id'],
            'title': 'Hello', 'body': 'my comment is awesome',
            'media': {}, 'role_id': detective.pk,
        })
    assert response.status_code == 200
    data = response.json()
    assert len(data['comments']) == 2
    comment = data['comments'][1]
    # create a game
    client = django_client.Client()
    client.login(
        username=superuser.user.username, password=superuser.user.username)
    response = client.post(f'/games/add_game/{variation.pk}/', {
        'serial_number': 1, 'name': variation.name
    })
    assert response.status_code == 302
    game_id = re.match(r'/games/edit_game/(\w+)/main/', response.url).group(1)
    # get game link
    response = superuser.get(f'/api/game_forum/game/{game_id}/')
    assert response.status_code == 200
    data = response.json()
    base_url = f'/api/game_forum/variation/{data["variation_id"]}/'
    room_id = data['thread_id']
    # get room
    response = superuser.get(base_url + f'thread/{room_id}/')
    assert response.status_code == 200
    room_data = response.json()
    assert len(room_data['threads']) == 2
    # check second thread
    assert room_data['threads'][1]['user']['title'] == detective.name
    assert room_data['threads'][1]['user']['id'] != detective.pk
    new_thread = room_data['threads'][0]
    # get thread rights
    response = superuser.get(
        base_url + f'thread/{new_thread["id"]}/granted_rights/')
    assert response.status_code == 200
    data = response.json()
    assert len(data['granted_rights']) == 1
    assert data['granted_rights'][0]['user']['title'] == detective.name
    assert data['granted_rights'][0]['user']['id'] != detective.pk
    # get comments
    response = superuser.get(thread1['url'] + 'comments_page/')
    assert response.status_code == 200
    data = response.json()
    assert len(data['comments']) == 2
    new_comment = data['comments'][1]
    assert new_comment['title'] == comment['title']
    assert new_comment['body'] == comment['body']
    assert new_comment['user']['title'] == comment['user']['title']
    assert new_comment['user']['id'] == comment['user']['id']


def test_create_game_creates_forum(variation, superuser):
    obj = stories_models.Variation.objects.get(pk=variation.pk)
    assert obj.thread_id is None
    # create a game
    client = django_client.Client()
    client.login(
        username=superuser.user.username, password=superuser.user.username)
    response = client.post(f'/games/add_game/{variation.pk}/', {
        'serial_number': 1, 'name': variation.name
    })
    assert response.status_code == 302
    game_id = re.match(r'/games/edit_game/(\w+)/main/', response.url).group(1)
    # get game link
    response = superuser.get(f'/api/game_forum/game/{game_id}/')
    assert response.status_code == 200
    data = response.json()
    base_url = f'/api/game_forum/variation/{data["variation_id"]}/'
    room_id = data['thread_id']
    # get room
    response = superuser.get(base_url + f'thread/{room_id}/')
    assert response.status_code == 200
    room_data = response.json()
    assert len(room_data['rooms']) == 0
