from django.db import transaction

from tulius.forum.threads import models
from tulius.games import models as game_models


def test_room_smoke(
        game, variation_forum, user, murderer, detective, admin):
    game.status = game_models.GAME_STATUS_IN_PROGRESS
    with transaction.atomic():
        game.save()
    # create room
    response = admin.put(
        variation_forum.get_absolute_url(), {
            'title': 'room', 'body': 'room description',
            'room': True, 'default_rights': models.ACCESS_READ,
            'granted_rights': []})
    assert response.status_code == 200


def test_threads_counters(game, variation_forum, user, detective, admin):
    game.status = game_models.GAME_STATUS_IN_PROGRESS
    with transaction.atomic():
        game.save()
    # create room
    response = admin.put(
        variation_forum.get_absolute_url(), {
            'title': 'room', 'body': 'room description',
            'room': True, 'default_rights': None,
            'granted_rights': []})
    assert response.status_code == 200
    room = response.json()
    # create hidden thread
    response = admin.put(
        room['url'], {
            'title': 'room', 'body': 'room description',
            'room': False, 'default_rights': models.NO_ACCESS,
            'granted_rights': [], 'media': {}, 'important': False})
    assert response.status_code == 200
    thread = response.json()
    # check initial counters state
    response = user.get(variation_forum.get_absolute_url())
    assert response.status_code == 200
    data = response.json()
    assert data['rooms'][0]['threads_count'] == 0
    # grant rights
    response = admin.post(
        thread['url'] + 'granted_rights/', {
            'user': {'id': detective.pk},
            'access_level': models.ACCESS_READ
        }
    )
    assert response.status_code == 200
    # check counters state
    response = user.get(variation_forum.get_absolute_url())
    assert response.status_code == 200
    data = response.json()
    assert data['rooms'][0]['threads_count'] == 1
