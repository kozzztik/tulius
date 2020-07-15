from xml.etree import ElementTree

import pytest
from django.db import transaction

from tulius.forum import models
from tulius.games import models as game_models


@pytest.mark.parametrize(
    'path', ['/sitemap-gameforum.xml', '/play/sitemap.xml'])
@pytest.mark.parametrize(
    'status', [
        game_models.GAME_STATUS_COMPLETED,
        game_models.GAME_STATUS_COMPLETED_OPEN])
def test_sitemap(game, variation_forum, client, path, superuser, status):
    game.status = game_models.GAME_STATUS_IN_PROGRESS
    with transaction.atomic():
        game.save()
    base_url = f'/api/game_forum/variation/{game.variation.id}/'
    # create thread with not set rights
    response = superuser.put(
        base_url + f'thread/{variation_forum.id}/', {
            'title': 'thread', 'body': 'thread description',
            'room': False, 'access_type': models.THREAD_ACCESS_TYPE_NOT_SET,
            'granted_rights': [], 'important': True, 'media': {}})
    assert response.status_code == 200
    thread = response.json()
    # create thread with no read access
    response = superuser.put(
        base_url + f'thread/{variation_forum.id}/', {
            'title': 'thread', 'body': 'thread description',
            'room': False, 'access_type': models.THREAD_ACCESS_TYPE_NO_READ,
            'granted_rights': [], 'important': True, 'media': {}})
    assert response.status_code == 200
    thread2 = response.json()
    # switch game status
    game.status = status
    with transaction.atomic():
        game.save()
    # retrieve sitemap
    response = client.get(path)
    assert response.status_code == 200
    data = ElementTree.fromstring(response.content)
    # check contents
    found = False
    for thread_data in data:
        loc = thread_data[0].text
        # check that rooms and "no read" threads are not in sitemap
        assert loc != f'http://example.com/play/thread/{variation_forum.pk}/'
        assert loc != f'http://example.com/play/thread/{thread2["id"]}/'
        if status == game_models.GAME_STATUS_COMPLETED_OPEN:
            if loc == f'http://example.com/play/thread/{thread["id"]}/':
                found = True
        else:
            assert loc != f'http://example.com/play/thread/{thread["id"]}/'
    assert found == (status == game_models.GAME_STATUS_COMPLETED_OPEN)
