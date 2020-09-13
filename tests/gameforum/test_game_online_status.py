from django.db import transaction
from django.conf import settings

from redis import client as redis_client

from tulius.games import models as game_models
from tulius.gameforum import online_status
from tulius.forum import online_status as forum_online



def test_game_online_status(
        game, variation_forum, user, admin, detective, client):
    # cleanup caches
    redis = redis_client.Redis(**settings.REDIS_CONNECTION)
    redis.delete(
        forum_online.thread_key(variation_forum.__class__, variation_forum.pk))
    game.status = game_models.GAME_STATUS_IN_PROGRESS
    with transaction.atomic():
        game.save()
    # get online roles by admin, should be empty
    response = admin.get(
        variation_forum.get_absolute_url() + 'online_status/')
    assert response.status_code == 200
    data = response.json()
    assert data['users'] == []
    data = online_status.get_online_roles(game.variation)
    assert list(data) == []
    # get online roles by user
    response = user.get(
        variation_forum.get_absolute_url() + 'online_status/')
    assert response.status_code == 200
    data = response.json()
    assert len(data['users']) == 1
    assert data['users'][0]['id'] == detective.pk
    assert data['users'][0]['title'] == detective.name
    data = list(online_status.get_online_roles(game.variation))
    assert data == [detective]
    # check anonymous request
    response = client.get(
        variation_forum.get_absolute_url() + 'online_status/')
    assert response.status_code == 200
    data = response.json()
    assert len(data['users']) == 1
    assert data['users'][0]['id'] == detective.pk
