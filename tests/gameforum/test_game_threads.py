from django.db import transaction

from tulius.forum.threads import models
from tulius.games import models as game_models


def test_room_smoke(
        game, variation_forum, user, murderer, detective, admin):
    game.status = game_models.GAME_STATUS_IN_PROGRESS
    with transaction.atomic():
        game.save()
    base_url = f'/api/game_forum/variation/{game.variation.id}/'
    # create room
    response = admin.put(
        base_url + f'thread/{variation_forum.id}/', {
            'title': 'room', 'body': 'room description',
            'room': True, 'default_rights': models.ACCESS_READ,
            'granted_rights': []})
    assert response.status_code == 200
