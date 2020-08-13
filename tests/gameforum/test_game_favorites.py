from django.db import transaction

from tulius.forum.threads import models
from tulius.games import models as game_models


def test_game_favorites(game, variation_forum, user, admin, detective):
    game.status = game_models.GAME_STATUS_IN_PROGRESS
    with transaction.atomic():
        game.save()
    base_url = f'/api/game_forum/variation/{game.variation.id}/'
    # create thread to like
    response = admin.put(
        base_url + f'thread/{variation_forum.id}/', {
            'title': 'thread', 'body': 'thread description',
            'room': False, 'default_rights': None,
            'granted_rights': [], 'important': False, 'media': {}})
    assert response.status_code == 200
    thread = response.json()
    # get favorites, check empty
    response = user.get('/api/game_forum/favorites/')
    assert response.status_code == 200
    data = response.json()
    assert data['groups'] == []
    # do like
    response = user.post(
        base_url + 'likes/',
        {'id': thread['first_comment_id'], 'value': True})
    assert response.status_code == 200
    # check favorites again
    response = user.get('/api/game_forum/favorites/')
    assert response.status_code == 200
    data = response.json()
    item = data['groups'][0]
    assert item['name'] == game.variation.name
    assert item['items'][0]['comment']['id'] == thread['first_comment_id']
    assert item['items'][0]['comment']['user']['id'] is None
    assert item['items'][0]['comment']['user']['title'] == '---'
