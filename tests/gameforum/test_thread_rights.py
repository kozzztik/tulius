from django.db import transaction

from tulius.games import models as game_models


def test_user_thread_api_rights(
        game, variation_forum, user, murderer, detective):
    game.status = game_models.GAME_STATUS_IN_PROGRESS
    with transaction.atomic():
        game.save()
    # Try to create thread without role specified. That is only for admins.
    response = user.put(
        variation_forum.get_absolute_url(), {
            'title': 'thread', 'body': 'thread description',
            'room': False, 'default_rights': None, 'granted_rights': [],
            'important': True, 'closed': True, 'media': {}})
    assert response.status_code == 403
    # try to create thread with not existing role
    response = user.put(
        variation_forum.get_absolute_url(), {
            'title': 'thread', 'body': 'thread description',
            'room': False, 'default_rights': None, 'granted_rights': [],
            'role_id': detective.pk + 1,
            'important': True, 'closed': True, 'media': {}})
    assert response.status_code == 403
    # smoke test - create a thread with right role.
    response = user.put(
        variation_forum.get_absolute_url(), {
            'title': 'thread', 'body': 'thread description',
            'room': False, 'default_rights': None, 'granted_rights': [],
            'role_id': detective.pk,
            'important': True, 'closed': True, 'media': {}})
    assert response.status_code == 200
    thread = response.json()
    assert not thread['important']
    assert not thread['closed']
    assert thread['user']['id'] == detective.pk
    assert thread['user']['title'] == detective.name
    # test update thread
    response = user.post(
        thread['url'], {
            'title': 'thread2', 'body': 'thread description2',
            'role_id': detective.pk, 'edit_role_id': detective.pk,
            'important': True, 'closed': True, 'media': {}})
    assert response.status_code == 200
    thread = response.json()
    assert thread['title'] == 'thread2'
    assert thread['body'] == 'thread description2'
    assert not thread['important']
    assert not thread['closed']
    assert thread['user']['id'] == detective.pk
    assert thread['user']['title'] == detective.name
    # try to update with wrong role
    response = user.post(
        thread['url'], {
            'title': 'thread2', 'body': 'thread description2',
            'role_id': murderer.pk, 'edit_role_id': detective.pk, 'media': {}})
    assert response.status_code == 403
    # try to update with wrong editor
    response = user.post(
        thread['url'], {
            'title': 'thread2', 'body': 'thread description2',
            'role_id': detective.pk, 'edit_role_id': murderer.pk, 'media': {}})
    assert response.status_code == 403
    # try to update with wrong editor & role
    response = user.post(
        thread['url'], {
            'title': 'thread2', 'body': 'thread description2',
            'role_id': murderer.pk, 'edit_role_id': murderer.pk, 'media': {}})
    assert response.status_code == 403
    # try to create room
    response = user.put(
        variation_forum.get_absolute_url(), {
            'title': 'room', 'body': 'room description',
            'room': True, 'default_rights': None, 'granted_rights': [],
            'role_id': detective.pk, 'media': {}})
    assert response.status_code == 200
    room = response.json()
    assert room['title'] == 'room'
    assert room['user']['id'] == detective.id
    # check how it looks on index
    response = user.get(variation_forum.get_absolute_url())
    assert response.status_code == 200
    data = response.json()
    assert len(data['rooms']) == 1
    assert len(data['threads']) == 1
    # check that role names correctly replaced
    assert data['rooms'][0]['user']['id'] == detective.pk
    assert data['threads'][0]['user']['id'] == detective.pk
    assert data['threads'][0]['user']['title'] == detective.name
    assert data['threads'][0]['last_comment']['user']['id'] == detective.pk
    assert data['threads'][0]['last_comment']['user']['title'] == \
           detective.name
