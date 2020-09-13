from django.db import transaction

from tulius.forum.threads import models
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
            'room': False, 'default_rights': models.NO_ACCESS,
            'granted_rights': [],
            'important': True, 'closed': True, 'media': {}})
    assert response.status_code == 200
    thread = response.json()
    # check guest can read it
    response = game_guest.get(thread['url'])
    assert response.status_code == 200
    data = response.json()
    assert data['body'] == 'thread description'
    # create thread with no specified rights. There was a problem with
    # fail on it
    response = admin.put(
        variation_forum.get_absolute_url(), {
            'title': 'thread', 'body': 'thread description',
            'room': False, 'default_rights': None,
            'granted_rights': [],
            'important': True, 'closed': True, 'media': {}})
    assert response.status_code == 200
    thread = response.json()
    # check guest can read it
    response = game_guest.get(thread['url'])
    assert response.status_code == 200


def test_finishing_game_rights(
        game, variation_forum, admin, user, detective, client):
    game.status = game_models.GAME_STATUS_IN_PROGRESS
    with transaction.atomic():
        game.save()
    # create thread with "no read" and no role
    response = admin.put(
        variation_forum.get_absolute_url(), {
            'title': 'thread', 'body': 'thread description',
            'room': False, 'default_rights': models.NO_ACCESS,
            'granted_rights': [],
            'important': False, 'media': {}})
    assert response.status_code == 200
    thread = response.json()
    # create own user thread
    response = user.put(
        variation_forum.get_absolute_url(), {
            'title': 'thread', 'body': 'thread description',
            'room': False, 'default_rights': models.NO_ACCESS,
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
            'room': False, 'default_rights': models.ACCESS_OPEN,
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
            'access_level': models.ACCESS_MODERATE
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
            'room': True, 'default_rights': models.NO_ACCESS,
            'granted_rights': [], 'media': {}})
    assert response.status_code == 200
    room = response.json()
    # create thread with "no read" and no role and detective grants
    response = admin.put(
        room['url'], {
            'title': 'thread', 'body': 'thread description',
            'room': False, 'default_rights': models.NO_ACCESS,
            'granted_rights': [{
                'user': {'id': detective.pk},
                'access_level': models.ACCESS_READ
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
            'access_level': models.ACCESS_READ
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
            'room': True, 'default_rights': models.ACCESS_READ,
            'granted_rights': [], 'media': {}})
    assert response.status_code == 200
    room = response.json()
    # create middle room with "not set" type and write rights
    response = admin.put(
        room['url'], {
            'title': 'room', 'body': 'room description',
            'room': True, 'default_rights': None,
            'granted_rights': [], 'media': {}})
    assert response.status_code == 200
    room2 = response.json()
    # create thread with "no read" and no role and detective grants
    response = admin.put(
        room2['url'], {
            'title': 'thread', 'body': 'thread description',
            'room': False, 'default_rights': models.NO_ACCESS,
            'granted_rights': [{
                'user': {'id': detective.pk},
                'access_level': models.ACCESS_READ
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
            'access_level': models.ACCESS_WRITE
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
            'room': True, 'default_rights': models.ACCESS_READ,
            'granted_rights': [], 'media': {}})
    assert response.status_code == 200
    thread = response.json()
    # break forum tree
    game.variation.thread = core.create_game_forum(admin.user, game.variation)
    game.variation.save()
    # now get thread. Previously it caused 500 on tree rights check.
    response = admin.get(thread['url'])
    assert response.status_code == 200


def test_grant_rights_to_variation(variation, variation_forum, user):
    response = user.get(variation_forum.get_absolute_url())
    assert response.status_code == 403
    # grant rights
    admin = story_models.StoryAdmin(story=variation.story, user=user.user)
    admin.save()
    # check
    response = user.get(variation_forum.get_absolute_url())
    assert response.status_code == 200
    # delete
    admin.delete()
    response = user.get(variation_forum.get_absolute_url())
    assert response.status_code == 403


def test_grant_rights_to_game(game, variation_forum, user):
    game.status = game_models.GAME_STATUS_IN_PROGRESS
    with transaction.atomic():
        game.save()
    response = user.get(variation_forum.get_absolute_url())
    assert response.status_code == 403
    # grant rights
    admin = game_models.GameAdmin(game=game, user=user.user)
    admin.save()
    # check
    response = user.get(variation_forum.get_absolute_url())
    assert response.status_code == 200
    response = user.put(
        variation_forum.get_absolute_url(), {
            'title': 'room', 'body': 'room description',
            'room': True, 'default_rights': models.ACCESS_READ,
            'granted_rights': [], 'media': {}})
    assert response.status_code == 200
    # delete
    admin.delete()
    response = user.get(variation_forum.get_absolute_url())
    assert response.status_code == 403
    # grant guest rights
    guest = game_models.GameGuest(game=game, user=user.user)
    guest.save()
    # check
    response = user.get(variation_forum.get_absolute_url())
    assert response.status_code == 200
    response = user.put(
        variation_forum.get_absolute_url(), {
            'title': 'room', 'body': 'room description',
            'room': True, 'default_rights': models.ACCESS_READ,
            'granted_rights': [], 'media': {}})
    assert response.status_code == 403
    # delete
    guest.delete()
    response = user.get(variation_forum.get_absolute_url())
    assert response.status_code == 403


def test_not_inherited_read_only_root(
        game, variation_forum, user, admin, detective):
    response = admin.put(
        variation_forum.get_absolute_url() + 'granted_rights/',
        {'default_rights': models.ACCESS_READ + models.ACCESS_NO_INHERIT})
    assert response.status_code == 200
    # create sub room
    response = admin.put(
        variation_forum.get_absolute_url(), {
            'title': 'room', 'body': 'room description',
            'room': True, 'default_rights': None,
            'granted_rights': [], 'media': {}})
    assert response.status_code == 200
    room = response.json()
    # start game. Reload game to update thread caches.
    game = game_models.Game.objects.get(pk=game.pk)
    game.status = game_models.GAME_STATUS_IN_PROGRESS
    with transaction.atomic():
        game.save()
    # check user can read and can't write at root
    response = user.get(variation_forum.get_absolute_url())
    assert response.status_code == 200
    response = user.put(
        variation_forum.get_absolute_url(), {
            'title': 'room', 'body': 'room description',
            'room': True, 'default_rights': None, 'role_id': detective.pk,
            'granted_rights': [], 'media': {}})
    assert response.status_code == 403
    # check we can read and write in sub room
    response = user.get(room['url'])
    assert response.status_code == 200
    response = user.put(
        room['url'], {
            'title': 'room', 'body': 'room description',
            'room': True, 'default_rights': None, 'role_id': detective.pk,
            'granted_rights': [], 'media': {}})
    assert response.status_code == 200


def test_not_inherited_read_only_room(
        game, variation_forum, user, admin, detective):
    # create sub room
    response = admin.put(
        variation_forum.get_absolute_url(), {
            'title': 'room', 'body': 'room description',
            'room': True,
            'default_rights': models.ACCESS_READ + models.ACCESS_NO_INHERIT,
            'granted_rights': [], 'media': {}})
    assert response.status_code == 200
    room1 = response.json()
    # create sub sub room
    response = admin.put(
        variation_forum.get_absolute_url(), {
            'title': 'room', 'body': 'room description',
            'room': True, 'default_rights': None,
            'granted_rights': [], 'media': {}})
    assert response.status_code == 200
    room2 = response.json()
    # start game
    game.status = game_models.GAME_STATUS_IN_PROGRESS
    with transaction.atomic():
        game.save()
    # check we can read and write in root
    response = user.get(variation_forum.get_absolute_url())
    assert response.status_code == 200
    response = user.put(
        variation_forum.get_absolute_url(), {
            'title': 'room', 'body': 'room description',
            'room': True, 'default_rights': None, 'role_id': detective.pk,
            'granted_rights': [], 'media': {}})
    assert response.status_code == 200
    # check user can read and can't write at room
    response = user.get(room1['url'])
    assert response.status_code == 200
    response = user.put(
        room1['url'], {
            'title': 'room', 'body': 'room description',
            'room': True, 'default_rights': None, 'role_id': detective.pk,
            'granted_rights': [], 'media': {}})
    assert response.status_code == 403
    # check we can read and write in sub room
    response = user.get(room2['url'])
    assert response.status_code == 200
    response = user.put(
        room2['url'], {
            'title': 'room', 'body': 'room description',
            'room': True, 'default_rights': None, 'role_id': detective.pk,
            'granted_rights': [], 'media': {}})
    assert response.status_code == 200


def test_not_defined_rights_on_root(
        game, variation_forum, user, admin, detective):
    response = admin.put(
        variation_forum.get_absolute_url() + 'granted_rights/',
        {'default_rights': None})
    assert response.status_code == 200
    # start game. Reload game to update thread caches.
    game = game_models.Game.objects.get(pk=game.pk)
    game.status = game_models.GAME_STATUS_IN_PROGRESS
    with transaction.atomic():
        game.save()
    # check user can read and write at root
    response = user.get(variation_forum.get_absolute_url())
    assert response.status_code == 200
    response = user.put(
        variation_forum.get_absolute_url(), {
            'title': 'room', 'body': 'room description',
            'room': True, 'default_rights': None, 'role_id': detective.pk,
            'granted_rights': [], 'media': {}})
    assert response.status_code == 200


def test_rights_override(game, variation_forum, user, admin, detective):
    game.status = game_models.GAME_STATUS_IN_PROGRESS
    with transaction.atomic():
        game.save()
    response = admin.put(
        variation_forum.get_absolute_url(), {
            'title': 'room', 'body': 'room description',
            'room': True, 'default_rights': models.ACCESS_READ,
            'role_id': None,
            'granted_rights': [], 'media': {}})
    assert response.status_code == 200
    room1 = response.json()
    response = admin.put(
        room1['url'], {
            'title': 'room2', 'body': 'room2 description',
            'room': True, 'default_rights': models.ACCESS_OPEN,
            'role_id': None,
            'granted_rights': [], 'media': {}})
    assert response.status_code == 200
    room2 = response.json()
    # check no write room1
    response = user.put(
        room1['url'], {
            'title': 'thread', 'body': 'thread description',
            'room': False, 'default_rights': None, 'role_id': detective.pk,
            'granted_rights': [], 'media': {}})
    assert response.status_code == 403
    # check write room2
    response = user.put(
        room2['url'], {
            'title': 'thread', 'body': 'thread description',
            'room': False, 'default_rights': None, 'role_id': detective.pk,
            'granted_rights': [], 'media': {}})
    assert response.status_code == 200
