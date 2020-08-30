from django.db import transaction

from tulius.forum.threads import models
from tulius.games import models as game_models


def test_thread_rights_api(
        game, variation_forum, user, murderer, detective, admin):
    game.status = game_models.GAME_STATUS_IN_PROGRESS
    with transaction.atomic():
        game.save()
    base_url = f'/api/game_forum/variation/{game.variation.id}/'
    # create thread with "no read" and no role
    response = admin.put(
        base_url + f'thread/{variation_forum.id}/', {
            'title': 'thread', 'body': 'thread description',
            'room': False, 'default_rights': models.NO_ACCESS,
            'granted_rights': [],
            'important': True, 'closed': True, 'media': {}})
    assert response.status_code == 200
    thread = response.json()
    assert thread['important']
    assert not thread['closed']
    # check user not see it in room
    response = user.get(base_url + f'thread/{variation_forum.id}/')
    assert response.status_code == 200
    data = response.json()
    assert not data['rooms']
    assert not data['threads']
    # check direct get
    response = user.get(thread['url'])
    assert response.status_code == 403
    # grant permissions
    response = admin.post(
        thread['url'] + 'granted_rights/', {
            'user': {'id': detective.pk},
            'access_level': models.ACCESS_READ
        }
    )
    assert response.status_code == 200
    # check it is now in list
    response = admin.get(thread['url'] + 'granted_rights/')
    assert response.status_code == 200
    rights = response.json()
    assert len(rights['granted_rights']) == 1
    assert rights['granted_rights'][0]['user']['id'] == detective.pk
    assert rights['granted_rights'][0]['user']['title'] == detective.name
    assert rights['granted_rights'][0][
        'access_level'] == models.ACCESS_READ
    # check user now see it in room
    response = user.get(base_url + f'thread/{variation_forum.id}/')
    assert response.status_code == 200
    data = response.json()
    assert not data['rooms']
    assert len(data['threads']) == 1
    assert data['threads'][0]['id'] == thread['id']
    assert data['threads'][0]['url'] == thread['url']
    assert data['rights']['user_write_roles'] == [detective.pk]
    assert data['rights']['write']
    # check user can access
    response = user.get(thread['url'])
    assert response.status_code == 200
    data = response.json()
    assert data['rights']['user_write_roles'] == []
    assert not data['rights']['write']
    # now drop rights
    response = admin.delete(rights['granted_rights'][0]['url'])
    assert response.status_code == 200
    # check user now have no access
    response = user.get(thread['url'])
    assert response.status_code == 403
    # create thread with access already on place
    response = admin.put(
        base_url + f'thread/{variation_forum.id}/', {
            'title': 'thread', 'body': 'thread description',
            'room': False, 'default_rights': models.NO_ACCESS,
            'granted_rights': [{
                'user': {'id': detective.pk},
                'access_level': models.ACCESS_READ
            }],
            'important': True, 'closed': True, 'media': {}})
    assert response.status_code == 200
    thread2 = response.json()
    # check user see it in room and dont see previous one
    response = user.get(base_url + f'thread/{variation_forum.id}/')
    assert response.status_code == 200
    data = response.json()
    assert not data['rooms']
    assert len(data['threads']) == 1
    assert data['threads'][0]['id'] == thread2['id']
    # check access
    response = user.get(thread2['url'])
    assert response.status_code == 200
