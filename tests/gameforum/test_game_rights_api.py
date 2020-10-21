import re

from django.db import transaction
from django.test import client as django_client

from tulius.forum.threads import models
from tulius.games import models as game_models
from tulius.stories import models as story_models


def test_thread_rights_api(
        game, variation_forum, user, murderer, detective, admin):
    game.status = game_models.GAME_STATUS_IN_PROGRESS
    with transaction.atomic():
        game.save()
    # create thread with "no read" and no role
    response = admin.put(
        variation_forum.get_absolute_url(), {
            'title': 'thread', 'body': 'thread description',
            'room': False, 'default_rights': models.NO_ACCESS,
            'granted_rights': [],
            'important': True, 'closed': True, 'media': {}})
    assert response.status_code == 200
    thread = response.json()
    assert thread['important']
    assert not thread['closed']
    # check user not see it in room
    response = user.get(variation_forum.get_absolute_url())
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
    response = user.get(variation_forum.get_absolute_url())
    assert response.status_code == 200
    data = response.json()
    assert not data['rooms']
    assert len(data['threads']) == 1
    assert data['threads'][0]['id'] == thread['id']
    assert data['threads'][0]['url'] == thread['url']
    assert data['rights']['user_write_roles'] == [detective.pk]
    assert data['rights']['write']
    assert data['rights']['strict_read'] is None
    # check user can access
    response = user.get(thread['url'])
    assert response.status_code == 200
    data = response.json()
    assert data['rights']['user_write_roles'] == []
    assert not data['rights']['write']
    assert data['rights']['strict_read'] == [detective.pk]
    # now drop rights
    response = admin.delete(rights['granted_rights'][0]['url'])
    assert response.status_code == 200
    # check user now have no access
    response = user.get(thread['url'])
    assert response.status_code == 403
    # create thread with access already on place
    response = admin.put(
        variation_forum.get_absolute_url(), {
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
    response = user.get(variation_forum.get_absolute_url())
    assert response.status_code == 200
    data = response.json()
    assert not data['rooms']
    assert len(data['threads']) == 1
    assert data['threads'][0]['id'] == thread2['id']
    # check access
    response = user.get(thread2['url'])
    assert response.status_code == 200


def test_role_assign_after_thread_create(
        game, variation_forum, user, detective, admin):
    detective.user = None
    detective.save()
    # create thread with access already on place
    response = admin.put(
        variation_forum.get_absolute_url(), {
            'title': 'thread', 'body': 'thread description',
            'room': False, 'default_rights': models.NO_ACCESS,
            'granted_rights': [{
                'user': {'id': detective.pk},
                'access_level': models.ACCESS_READ
            }],
            'important': True, 'media': {}})
    assert response.status_code == 200
    thread = response.json()

    game.status = game_models.GAME_STATUS_IN_PROGRESS
    with transaction.atomic():
        game.save()

    # check user have no access
    response = user.get(variation_forum.get_absolute_url())
    assert response.status_code == 403

    # assign to role
    response = admin.post(f'/games/role/{detective.pk}/assign{user.user.pk}/')
    assert response.status_code == 302
    # check
    obj = detective.__class__.objects.get(pk=detective.pk)
    assert obj.user == user.user

    # check user see it in room
    response = user.get(variation_forum.get_absolute_url())
    assert response.status_code == 200
    data = response.json()
    assert not data['rooms']
    assert len(data['threads']) == 1
    assert data['threads'][0]['id'] == thread['id']


def test_game_create_full_cycle(
        variation, variation_forum, user, detective, admin, superuser):
    detective.user = None
    detective.save()
    # create room
    response = admin.put(
        variation_forum.get_absolute_url(), {
            'title': 'room', 'body': 'room description',
            'room': True, 'default_rights': None,
            'granted_rights': []})
    assert response.status_code == 200
    room = response.json()

    # create thread with access already on place
    response = admin.put(
        room['url'], {
            'title': 'thread', 'body': 'thread description',
            'room': False, 'default_rights': models.NO_ACCESS,
            'granted_rights': [{
                'user': {'id': detective.pk},
                'access_level': models.ACCESS_READ
            }],
            'important': True, 'media': {}})
    assert response.status_code == 200

    client = django_client.Client()
    client.login(
        username=superuser.user.username, password=superuser.user.username)
    response = client.post(f'/games/add_game/{variation.pk}/', {
        'serial_number': 1,
        'name': variation.name,
    })
    assert response.status_code == 302
    game_id = re.match(r'/games/edit_game/(\w+)/main/', response.url).group(1)
    game = game_models.Game.objects.get(pk=game_id)
    detective = story_models.Role.objects.get(variation=game.variation)

    # assign to role
    response = superuser.post(
        f'/games/role/{detective.pk}/assign{user.user.pk}/')
    assert response.status_code == 302
    # check
    obj = detective.__class__.objects.get(pk=detective.pk)
    assert obj.user == user.user

    game.status = game_models.GAME_STATUS_IN_PROGRESS
    with transaction.atomic():
        game.save()

    # check we see thread count correctly (there was a problem before)
    response = user.get(game.variation.thread.get_absolute_url())
    assert response.status_code == 200
    data = response.json()
    assert data['rooms'][0]['rooms_count'] == 0
    assert data['rooms'][0]['threads_count'] == 1
