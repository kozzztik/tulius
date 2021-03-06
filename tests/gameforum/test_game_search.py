from django.db import transaction
from django.db.models import signals

from tulius.games import models as game_models
from tulius.gameforum.comments import models
from tulius.forum.elastic_search import models as es_models


def test_options(game, variation_forum, user, admin, detective, murderer):
    base_url = f'/api/game_forum/variation/{game.variation.id}/'
    response = user.options(base_url + 'search/?query=' + murderer.name[:3])
    assert response.status_code == 200
    data = response.json()
    assert len(data['users']) == 1
    assert data['users'][0]['id'] == murderer.id
    assert data['users'][0]['title'] == murderer.name
    pks = f'{detective.pk},0'
    response = user.options(base_url + 'search/?pks=' + pks)
    assert response.status_code == 200
    data = response.json()
    assert len(data['users']) == 2
    users = {u['id']: u for u in data['users']}
    assert users[detective.pk]['title'] == detective.name
    assert users[0]['title'] == '---'


def test_game_search(game, variation_forum, user, admin, detective, murderer):
    game.status = game_models.GAME_STATUS_IN_PROGRESS
    with transaction.atomic():
        game.save()
    base_url = f'/api/game_forum/variation/{game.variation.id}/'
    # create thread
    response = admin.put(
        base_url + f'thread/{variation_forum.id}/', {
            'title': 'thread', 'body': 'thread description',
            'room': False, 'default_rights': None,
            'granted_rights': [], 'important': False, 'media': {}})
    assert response.status_code == 200
    thread = response.json()
    # create detective comment
    response = user.post(
        thread['url'] + 'comments_page/', {
            'reply_id': thread['first_comment_id'],
            'title': 'Got it', 'body': 'I found a murderer!',
            'media': {}, 'role_id': detective.pk,
        })
    assert response.status_code == 200
    data = response.json()
    comment1 = data['comments'][1]
    # create murderer comment
    response = admin.post(
        thread['url'] + 'comments_page/', {
            'reply_id': thread['first_comment_id'],
            'title': 'Got it', 'body': 'That is not me!',
            'media': {}, 'role_id': murderer.pk,
        })
    assert response.status_code == 200
    data = response.json()
    comment2 = data['comments'][2]
    # search smoke test
    response = user.post(
        base_url + 'search/', {'thread_id': thread["id"]})
    assert response.status_code == 200
    data = response.json()
    assert len(data['results']) == 3
    # search detective
    response = user.post(
        base_url + 'search/',
        {'users': [detective.pk], 'thread_id': thread["id"]})
    assert response.status_code == 200
    data = response.json()
    assert len(data['results']) == 1
    assert data['results'][0]['comment']['id'] == comment1['id']
    item = data['results'][0]['comment']
    assert item['user']['id'] == detective.pk
    assert item['user']['title'] == detective.name
    # search not murderer
    response = user.post(
        base_url + 'search/',
        {'not_users': [murderer.pk], 'thread_id': thread["id"]})
    assert response.status_code == 200
    data = response.json()
    assert len(data['results']) == 2
    # ordering in responses sometimes may be different, so fix it for checks
    data['results'].sort(key=lambda x: x['comment']['id'])
    assert data['results'][0]['comment']['id'] == thread['first_comment_id']
    assert data['results'][1]['comment']['id'] == comment1['id']
    # check search leader comments
    response = user.post(
        base_url + 'search/',
        {'users': [0], 'thread_id': thread["id"]})
    assert response.status_code == 200
    data = response.json()
    assert len(data['results']) == 1
    assert data['results'][0]['comment']['id'] == thread['first_comment_id']
    # check filter leader comments
    response = user.post(
        base_url + 'search/',
        {'not_users': [0], 'thread_id': thread["id"]})
    assert response.status_code == 200
    data = response.json()
    assert len(data['results']) == 2
    assert data['results'][0]['comment']['id'] == comment1['id']
    assert data['results'][1]['comment']['id'] == comment2['id']


def setup_module(module):
    signals.post_save.connect(es_models.do_direct_index, sender=models.Comment)


def teardown_module(module):
    """ teardown any state that was previously setup with a setup_module
    method.
    """
    assert signals.post_save.disconnect(
        es_models.do_direct_index, sender=models.Comment)
