from django.db import transaction

from tulius.forum.threads import models
from tulius.forum.rights import models as rights_models
from tulius.games import models as game_models
from tulius.stories import models as story_models
from tulius.gameforum import core


def test_thread_with_wrong_variation(
        story, game, admin, variation_forum):
    variation = story_models.Variation(story=story, name='Variation2')
    variation.save()
    base_url = f'/api/game_forum/variation/{variation.pk}/'
    response = admin.get(base_url + f'thread/{variation_forum.pk}/')
    assert response.status_code == 403


def test_access_to_variation(variation, variation_forum, client, user):
    base_url = f'/api/game_forum/variation/{variation.pk}/'
    response = client.get(base_url + f'thread/{variation_forum.pk}/')
    assert response.status_code == 403
    response = user.get(base_url + f'thread/{variation_forum.pk}/')
    assert response.status_code == 403


def test_guest_access_to_game(game, variation_forum, admin, game_guest):
    game.status = game_models.GAME_STATUS_IN_PROGRESS
    with transaction.atomic():
        game.save()
    # create thread with "no read" and no role
    response = admin.put(
        variation_forum.get_absolute_url(), {
            'title': 'thread', 'body': 'thread description',
            'room': False, 'access_type': models.THREAD_ACCESS_TYPE_NO_READ,
            'granted_rights': [],
            'important': True, 'closed': True, 'media': {}})
    assert response.status_code == 200
    thread = response.json()
    # check guest can read it
    response = game_guest.get(thread['url'])
    assert response.status_code == 200
    data = response.json()
    assert data['body'] == 'thread description'


def test_finishing_game_rights(
        game, variation_forum, admin, user, detective, client):
    game.status = game_models.GAME_STATUS_IN_PROGRESS
    with transaction.atomic():
        game.save()
    # create thread with "no read" and no role
    response = admin.put(
        variation_forum.get_absolute_url(), {
            'title': 'thread', 'body': 'thread description',
            'room': False, 'access_type': models.THREAD_ACCESS_TYPE_NO_READ,
            'granted_rights': [],
            'important': False, 'media': {}})
    assert response.status_code == 200
    thread = response.json()
    # create own user thread
    response = user.put(
        variation_forum.get_absolute_url(), {
            'title': 'thread', 'body': 'thread description',
            'room': False, 'access_type': models.THREAD_ACCESS_TYPE_NO_READ,
            'granted_rights': [], 'role_id': detective.pk, 'media': {}})
    assert response.status_code == 200
    thread2 = response.json()
    # check user can add comments
    response = user.post(
        thread2['url'] + 'comments_page/', {
            'reply_id': thread2['first_comment_id'],
            'title': 'Hello', 'body': 'my comment is awesome',
            'media': {}, 'role_id': detective.pk,
        })
    assert response.status_code == 200
    data = response.json()
    assert len(data['comments']) == 2
    # check user can't read first thread
    response = user.get(thread['url'])
    assert response.status_code == 403
    # change game status
    game.status = game_models.GAME_STATUS_FINISHING
    with transaction.atomic():
        game.save()
    # check user still can write
    response = user.post(
        thread2['url'] + 'comments_page/', {
            'reply_id': thread2['first_comment_id'],
            'title': 'Hello', 'body': 'my comment is awesome',
            'media': {}, 'role_id': detective.pk,
        })
    assert response.status_code == 200
    data = response.json()
    assert len(data['comments']) == 3
    # And thread is opened now
    response = user.get(thread['url'])
    assert response.status_code == 200
    # Finish game
    game.status = game_models.GAME_STATUS_COMPLETED
    with transaction.atomic():
        game.save()
    # check user can't write any more
    response = user.post(
        thread2['url'] + 'comments_page/', {
            'reply_id': thread2['first_comment_id'],
            'title': 'Hello', 'body': 'my comment is awesome',
            'media': {}, 'role_id': detective.pk,
        })
    assert response.status_code == 403
    # Thread is still opened
    response = user.get(thread['url'])
    assert response.status_code == 200
    # but still not for anonymous
    response = client.get(thread['url'])
    assert response.status_code == 403
    # Open game
    game.status = game_models.GAME_STATUS_COMPLETED_OPEN
    with transaction.atomic():
        game.save()
    # now anyone can read
    response = client.get(thread['url'])
    assert response.status_code == 200


def test_grant_moderator_rights(game, variation_forum, admin, user, detective):
    game.status = game_models.GAME_STATUS_IN_PROGRESS
    with transaction.atomic():
        game.save()
    base_url = f'/api/game_forum/variation/{game.variation.pk}/'
    # create thread with "no read" and no role
    response = admin.put(
        base_url + f'thread/{variation_forum.id}/', {
            'title': 'thread', 'body': 'thread description',
            'room': False, 'access_type': models.THREAD_ACCESS_TYPE_OPEN,
            'granted_rights': [], 'important': False, 'media': {}})
    assert response.status_code == 200
    thread = response.json()
    # add a comment by admin
    response = admin.post(
        thread['url'] + 'comments_page/', {
            'reply_id': thread['first_comment_id'],
            'title': 'Hello', 'body': 'my comment is awesome',
            'media': {}, 'role_id': detective.pk,
        })
    assert response.status_code == 200
    data = response.json()
    assert len(data['comments']) == 2
    comment = data['comments'][1]
    # check user can read thread and cant edit comment
    response = user.get(thread['url'])
    assert response.status_code == 200
    data = response.json()
    assert data['body'] == 'thread description'
    response = user.post(comment['url'], {
        'title': 'Hello', 'body': 'my comment is awesome2',
        'media': {}, 'role_id': detective.pk})
    assert response.status_code == 403
    # grant moderate rights
    response = admin.post(
        thread['url'] + 'granted_rights/', {
            'user': {'id': detective.pk},
            'access_level': rights_models.THREAD_ACCESS_MODERATE
        }
    )
    assert response.status_code == 200
    # check we can update comment
    response = user.post(comment['url'], {
        'title': 'Hello', 'body': 'my comment is awesome2',
        'media': {}, 'role_id': detective.pk, 'edit_role_id': detective.pk})
    assert response.status_code == 200
    data = response.json()
    assert data['body'] == 'my comment is awesome2'


def test_chain_strict_read(
        game, variation_forum, admin, user, detective, murderer):
    game.status = game_models.GAME_STATUS_IN_PROGRESS
    with transaction.atomic():
        game.save()
    # create room with read limits
    response = admin.put(
        variation_forum.get_absolute_url(), {
            'title': 'room', 'body': 'room description',
            'room': True, 'access_type': models.THREAD_ACCESS_TYPE_NO_READ,
            'granted_rights': [], 'media': {}})
    assert response.status_code == 200
    room = response.json()
    # create thread with "no read" and no role and detective grants
    response = admin.put(
        room['url'], {
            'title': 'thread', 'body': 'thread description',
            'room': False, 'access_type': models.THREAD_ACCESS_TYPE_NO_READ,
            'granted_rights': [{
                'user': {'id': detective.pk},
                'access_level': rights_models.THREAD_ACCESS_READ
            }], 'important': False, 'media': {}})
    assert response.status_code == 200
    thread = response.json()
    # check user can read thread, because have exceptions, even have no access
    # to parent room.
    response = user.get(thread['url'])
    assert response.status_code == 200
    # and user don't see room
    response = user.get(variation_forum.get_absolute_url())
    assert response.status_code == 200
    data = response.json()
    assert not data['rooms']
    # but admin see it even if he play
    murderer.user = admin.user
    murderer.save()
    response = admin.get(variation_forum.get_absolute_url())
    assert response.status_code == 200
    data = response.json()
    assert len(data['rooms']) == 1
    # grant read rights to room
    response = admin.post(
        room['url'] + 'granted_rights/', {
            'user': {'id': detective.pk},
            'access_level': rights_models.THREAD_ACCESS_READ
        }
    )
    assert response.status_code == 200
    # check thread now
    response = user.get(thread['url'])
    assert response.status_code == 200
    data = response.json()
    assert data['body'] == 'thread description'
    # check root
    response = user.get(variation_forum.get_absolute_url())
    assert response.status_code == 200
    data = response.json()
    assert len(data['rooms']) == 1
    # check room
    response = user.get(room['url'])
    assert response.status_code == 200
    data = response.json()
    assert data['threads'][0]['accessed_users'][0]['id'] == detective.pk
    assert data['threads'][0]['accessed_users'][0]['title'] == detective.name


def test_chain_write_rights(game, variation_forum, admin, user, detective):
    game.status = game_models.GAME_STATUS_IN_PROGRESS
    with transaction.atomic():
        game.save()
    # create thread room with read limits
    response = admin.put(
        variation_forum.get_absolute_url(), {
            'title': 'room', 'body': 'room description',
            'room': True, 'access_type': models.THREAD_ACCESS_TYPE_NO_WRITE,
            'granted_rights': [], 'media': {}})
    assert response.status_code == 200
    room = response.json()
    # create middle room with "not set" type and write rights
    response = admin.put(
        room['url'], {
            'title': 'room', 'body': 'room description',
            'room': True, 'access_type': models.THREAD_ACCESS_TYPE_NOT_SET,
            'granted_rights': [], 'media': {}})
    assert response.status_code == 200
    room2 = response.json()
    # create thread with "no read" and no role and detective grants
    response = admin.put(
        room2['url'], {
            'title': 'thread', 'body': 'thread description',
            'room': False, 'access_type': models.THREAD_ACCESS_TYPE_NO_READ,
            'granted_rights': [{
                'user': {'id': detective.pk},
                'access_level': rights_models.THREAD_ACCESS_READ
            }], 'important': False, 'media': {}})
    assert response.status_code == 200
    thread = response.json()
    # check user can read thread
    response = user.get(thread['url'])
    assert response.status_code == 200
    # but can't write
    response = user.post(
        thread['url'] + 'comments_page/', {
            'reply_id': thread['first_comment_id'],
            'title': 'Hello', 'body': 'my comment is awesome',
            'media': {}, 'role_id': detective.pk,
        })
    assert response.status_code == 403
    # grant rights to middle room
    response = admin.post(
        room2['url'] + 'granted_rights/', {
            'user': {'id': detective.pk},
            'access_level': rights_models.THREAD_ACCESS_WRITE
        }
    )
    assert response.status_code == 200
    # and now still cant write
    response = user.post(
        thread['url'] + 'comments_page/', {
            'reply_id': thread['first_comment_id'],
            'title': 'Hello', 'body': 'my comment is awesome',
            'media': {}, 'role_id': detective.pk,
        })
    assert response.status_code == 403


def test_broken_tree_rights(game, variation_forum, admin):
    game.status = game_models.GAME_STATUS_IN_PROGRESS
    with transaction.atomic():
        game.save()
    base_url = f'/api/game_forum/variation/{game.variation.pk}/'
    # create thread room with read limits
    response = admin.put(
        base_url + f'thread/{variation_forum.id}/', {
            'title': 'room', 'body': 'room description',
            'room': True, 'access_type': models.THREAD_ACCESS_TYPE_NO_WRITE,
            'granted_rights': [], 'media': {}})
    assert response.status_code == 200
    thread = response.json()
    # break forum tree
    game.variation.thread = core.create_game_forum(admin.user, game.variation)
    game.variation.save()
    # now get thread. Previously it caused 500 on tree rights check.
    response = admin.get(thread['url'])
    assert response.status_code == 200
