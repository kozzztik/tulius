from django.db import transaction

from tulius.games import models as game_models
from tulius.gameforum import online_status


def test_game_online_status(
        game, variation_forum, user, admin, detective, client):
    game.status = game_models.GAME_STATUS_IN_PROGRESS
    with transaction.atomic():
        game.save()
    base_url = f'/api/game_forum/variation/{game.variation.id}/'
    # get online roles by admin, should be empty
    response = admin.get(
        base_url + f'thread/{variation_forum.pk}/online_status/')
    assert response.status_code == 200
    data = response.json()
    assert data['users'] == []
    data = online_status.get_online_roles(game.variation)
    assert list(data) == []
    # get online roles by user
    response = user.get(
        base_url + f'thread/{variation_forum.pk}/online_status/')
    assert response.status_code == 200
    data = response.json()
    assert len(data['users']) == 1
    assert data['users'][0]['id'] == detective.pk
    assert data['users'][0]['title'] == detective.name
    data = list(online_status.get_online_roles(game.variation))
    assert data == [detective]
    # check anonymous request
    response = client.get(
        base_url + f'thread/{variation_forum.pk}/online_status/')
    assert response.status_code == 200
    data = response.json()
    assert len(data['users']) == 1
    assert data['users'][0]['id'] == detective.pk
