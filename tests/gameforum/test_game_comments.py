from django.db import transaction

from tulius.forum.threads import models as forum_threads
from tulius.gameforum.threads import models as thread_models
from tulius.stories import models as story_models
from tulius.games import models as game_models


def test_comments_api(
        game, variation_forum, user, murderer, detective, admin):
    game.status = game_models.GAME_STATUS_IN_PROGRESS
    with transaction.atomic():
        game.save()
    base_url = f'/api/game_forum/variation/{game.variation.id}/'
    # create thread with "no read" and no role
    response = admin.put(
        variation_forum.get_absolute_url(), {
            'title': 'thread', 'body': 'thread description',
            'room': False,
            'default_rights': forum_threads.ACCESS_READ,
            'granted_rights': [], 'important': False, 'media': {}})
    assert response.status_code == 200
    thread = response.json()
    # try to add comment with user
    response = user.post(
        thread['url'] + 'comments_page/', {
            'reply_id': thread['first_comment_id'],
            'title': 'Hello', 'body': 'my comment is awesome',
            'media': {}, 'role_id': detective.pk,
        })
    assert response.status_code == 403
    # add rights to write
    response = admin.post(
        thread['url'] + 'granted_rights/', {
            'user': {'id': detective.pk},
            'access_level': forum_threads.ACCESS_WRITE
        }
    )
    assert response.status_code == 200
    # try again
    response = user.post(
        thread['url'] + 'comments_page/', {
            'reply_id': thread['first_comment_id'],
            'title': 'Hello', 'body': 'my comment is awesome',
            'media': {}, 'role_id': detective.pk,
        })
    assert response.status_code == 200
    data = response.json()
    comment = data['comments'][1]
    assert comment['title'] == 'Hello'
    assert comment['body'] == 'my comment is awesome'
    assert comment['user']['id'] == detective.pk
    assert comment['user']['title'] == detective.name
    # update comment
    response = user.post(
        comment['url'], {
            'reply_id': thread['first_comment_id'],
            'title': 'Hello', 'body': 'my comment is awesome2',
            'media': {}, 'role_id': detective.pk, 'edit_role_id': detective.pk,
        })
    assert response.status_code == 200
    data = response.json()
    assert data['body'] == 'my comment is awesome2'
    # try to update with wrong role
    response = user.post(
        comment['url'], {
            'reply_id': thread['first_comment_id'],
            'title': 'Hello', 'body': 'my comment is awesome3',
            'media': {}, 'role_id': murderer.pk, 'edit_role_id': detective.pk,
        })
    assert response.status_code == 403
    # try to update with wrong editor
    response = user.post(
        comment['url'], {
            'reply_id': thread['first_comment_id'],
            'title': 'Hello', 'body': 'my comment is awesome3',
            'media': {}, 'role_id': detective.pk, 'edit_role_id': murderer.pk,
        })
    assert response.status_code == 403
    # check body not changed in this attempts
    response = user.get(comment['url'])
    assert response.status_code == 200
    data = response.json()
    assert data['body'] == 'my comment is awesome2'
    assert data['user']['id'] == detective.pk
    # check comments counters
    response = admin.get(base_url)
    assert response.status_code == 200
    data = response.json()
    assert data['characters'][0]['id'] == murderer.pk
    assert data['characters'][0]['comments_count'] == 0
    assert data['characters'][1]['id'] == detective.pk
    assert data['characters'][1]['comments_count'] == 1
    variation = story_models.Variation.objects.get(pk=data['id'])
    assert variation.comments_count == 2
    # check role update works
    response = admin.post(
        comment['url'], {
            'reply_id': thread['first_comment_id'],
            'title': 'Hello', 'body': 'my comment is awesome3',
            'media': {}, 'role_id': murderer.pk, 'edit_role_id': detective.pk,
        })
    assert response.status_code == 200
    data = response.json()
    assert data['body'] == 'my comment is awesome3'
    assert data['user']['id'] == murderer.pk
    assert data['user']['title'] == murderer.name
    assert data['editor']['id'] == detective.pk
    assert data['editor']['title'] == detective.name
    # check comments counters again
    response = admin.get(base_url)
    assert response.status_code == 200
    data = response.json()
    assert data['characters'][0]['id'] == murderer.pk
    assert data['characters'][0]['comments_count'] == 1
    assert data['characters'][1]['id'] == detective.pk
    assert data['characters'][1]['comments_count'] == 0
    variation = story_models.Variation.objects.get(pk=data['id'])
    assert variation.comments_count == 2
    # delete comment
    response = user.delete(comment['url'] + '?comment=moo')
    assert response.status_code == 200
    # and check counters
    response = admin.get(base_url)
    assert response.status_code == 200
    data = response.json()
    assert data['characters'][0]['id'] == murderer.pk
    assert data['characters'][0]['comments_count'] == 0
    assert data['characters'][1]['id'] == detective.pk
    assert data['characters'][1]['comments_count'] == 0
    variation = story_models.Variation.objects.get(pk=data['id'])
    assert variation.comments_count == 1


def test_comments_illustrations(
        game, variation_forum, user, detective, story_illustration,
        variation_illustration):
    game.status = game_models.GAME_STATUS_IN_PROGRESS
    with transaction.atomic():
        game.save()
    base_url = f'/api/game_forum/variation/{game.variation.id}/'
    # create thread with illustration
    response = user.put(
        base_url + f'thread/{variation_forum.id}/', {
            'title': 'thread', 'body': 'thread description',
            'room': False,
            'default_rights': None,
            'granted_rights': [], 'role_id': detective.pk, 'media': {
                'illustrations': [{
                    'id': story_illustration.pk,
                    'foo': 'bar'
                }]
            }})
    assert response.status_code == 200
    thread = response.json()
    assert len(thread['media']['illustrations']) == 1
    entity = thread['media']['illustrations'][0]
    assert entity['id'] == story_illustration.pk
    assert entity['title'] == story_illustration.name
    # change illustration
    response = user.post(
        thread['url'], {
            'title': 'thread', 'body': 'thread description',
            'role_id': detective.pk, 'edit_role_id': detective.pk,
            'media': {'illustrations': [{
                'id': variation_illustration.pk,
                'foo': 'bar'
            }]}})
    assert response.status_code == 200
    thread = response.json()
    assert len(thread['media']['illustrations']) == 1
    entity = thread['media']['illustrations'][0]
    assert entity['id'] == variation_illustration.pk
    assert entity['title'] == variation_illustration.name
    # Do illustration delete
    response = user.post(
        thread['url'], {
            'title': 'thread', 'body': 'thread description',
            'role_id': detective.pk, 'edit_role_id': detective.pk,
            'media': {'illustrations': []}})
    assert response.status_code == 200
    thread = response.json()
    assert 'illustrations' not in thread['media']
    # try to add comment with illustration
    response = user.post(
        thread['url'] + 'comments_page/', {
            'reply_id': thread['first_comment_id'],
            'title': 'Hello', 'body': 'my comment is awesome',
            'role_id': detective.pk,
            'media': {
                'illustrations': [{
                    'id': story_illustration.pk,
                    'foo': 'bar'
                }]
            }})
    assert response.status_code == 200
    data = response.json()
    comment = data['comments'][1]
    assert len(comment['media']['illustrations']) == 1
    entity = comment['media']['illustrations'][0]
    assert entity['id'] == story_illustration.pk
    assert entity['title'] == story_illustration.name
    # change illustration
    response = user.post(
        comment['url'], {
            'reply_id': thread['first_comment_id'],
            'title': 'Hello', 'body': 'my comment is awesome',
            'role_id': detective.pk, 'edit_role_id': detective.pk,
            'media': {
                'illustrations': [{
                    'id': variation_illustration.pk,
                    'foo': 'bar'
                }]
            }})
    assert response.status_code == 200
    data = response.json()
    entity = data['media']['illustrations'][0]
    assert entity['id'] == variation_illustration.pk
    assert entity['title'] == variation_illustration.name
    # remove illustration from comment
    response = user.post(
        comment['url'], {
            'reply_id': thread['first_comment_id'],
            'title': 'Hello', 'body': 'my comment is awesome',
            'role_id': detective.pk, 'edit_role_id': detective.pk,
            'media': {
                'illustrations': []
            }})
    assert response.status_code == 200
    data = response.json()
    assert 'illustrations' not in data['media']


def test_broken_last_comment(game, variation_forum, user, detective):
    game.status = game_models.GAME_STATUS_IN_PROGRESS
    with transaction.atomic():
        game.save()
    base_url = f'/api/game_forum/variation/{game.variation.id}/'
    # create thread
    response = user.put(
        base_url + f'thread/{variation_forum.id}/', {
            'title': 'thread', 'body': 'thread description',
            'room': False,
            'default_rights': None,
            'granted_rights': [], 'role_id': detective.pk, 'media': {}
        })
    assert response.status_code == 200
    thread = response.json()
    # break last comment
    obj = thread_models.Thread.objects.get(pk=thread['id'])
    obj.last_comment[user.user.pk] += 1
    obj.save()
    # check room view still works
    response = user.get(base_url + f'thread/{variation_forum.id}/')
    assert response.status_code == 200
    data = response.json()
    assert 'last_comment' not in data['threads'][0]


def test_delete_game_comments_with_thread(
        game, variation_forum, detective, murderer, admin):
    game.status = game_models.GAME_STATUS_IN_PROGRESS
    with transaction.atomic():
        game.save()
    # create room
    response = admin.put(
        variation_forum.get_absolute_url(), {
            'title': 'thread', 'body': 'thread description',
            'room': True,
            'default_rights': None,
            'granted_rights': []})
    assert response.status_code == 200
    room = response.json()
    # create thread
    response = admin.put(
        room['url'], {
            'title': 'thread', 'body': 'thread description',
            'room': False,
            'default_rights': None,
            'granted_rights': [], 'role_id': detective.pk, 'media': {}
        })
    assert response.status_code == 200
    thread = response.json()
    # create second detective comment
    response = admin.post(
        thread['url'] + 'comments_page/', {
            'reply_id': thread['first_comment_id'],
            'title': 'Hello', 'body': 'my comment is awesome',
            'role_id': detective.pk,
            'media': {}})
    assert response.status_code == 200
    # create murderer comment
    response = admin.post(
        thread['url'] + 'comments_page/', {
            'reply_id': thread['first_comment_id'],
            'title': 'Hello', 'body': 'my comment is awesome',
            'role_id': murderer.pk,
            'media': {}})
    assert response.status_code == 200
    # check comments counts
    assert story_models.Role.objects.get(pk=detective.pk).comments_count == 2
    assert story_models.Role.objects.get(pk=murderer.pk).comments_count == 1
    # delete room
    response = admin.delete(room['url'] + '?comment=die')
    assert response.status_code == 200
    # check comments counts
    assert story_models.Role.objects.get(pk=detective.pk).comments_count == 0
    assert story_models.Role.objects.get(pk=murderer.pk).comments_count == 0


def test_game_comment_counters_on_rights_change(
        game, variation_forum, user, detective, admin):
    game.status = game_models.GAME_STATUS_IN_PROGRESS
    with transaction.atomic():
        game.save()
    # create room
    response = admin.put(
        variation_forum.get_absolute_url(), {
            'title': 'room', 'body': 'thread description',
            'room': True,
            'default_rights': None,
            'granted_rights': [], 'role_id': None, 'media': {}})
    assert response.status_code == 200
    room = response.json()
    # create room
    response = admin.put(
        room['url'], {
            'title': 'thread', 'body': 'thread description',
            'room': False,
            'default_rights': None,
            'granted_rights': [], 'role_id': None, 'media': {}})
    assert response.status_code == 200
    thread = response.json()
    # check initial state
    response = admin.get(variation_forum.get_absolute_url())
    assert response.status_code == 200
    data = response.json()
    assert data['rooms'][0]['last_comment']['id']
    assert data['rooms'][0]['comments_count'] == 1
    response = user.get(variation_forum.get_absolute_url())
    assert response.status_code == 200
    data = response.json()
    assert data['rooms'][0]['last_comment']['id']
    assert data['rooms'][0]['comments_count'] == 1
    # close thread
    response = admin.put(
        thread['url'] + 'granted_rights/', {
            'default_rights': forum_threads.NO_ACCESS})
    assert response.status_code == 200
    # check counters, admin still see
    response = admin.get(variation_forum.get_absolute_url())
    assert response.status_code == 200
    data = response.json()
    assert data['rooms'][0]['last_comment']['id']
    assert data['rooms'][0]['comments_count'] == 1
    # but anonymous user is not
    response = user.get(variation_forum.get_absolute_url())
    assert response.status_code == 200
    data = response.json()
    assert 'last_comment' not in data['rooms'][0]
    assert data['rooms'][0]['comments_count'] == 0


def test_game_comment_counters_on_thread_delete(
        game, variation_forum, user, detective, admin):
    game.status = game_models.GAME_STATUS_IN_PROGRESS
    with transaction.atomic():
        game.save()

    # Create room in root room
    response = admin.put(
        variation_forum.get_absolute_url(), {
            'title': 'room1', 'body': 'room1 description',
            'room': True, 'default_rights': None, 'role_id': None,
            'granted_rights': []})
    assert response.status_code == 200
    room = response.json()
    # create thread
    response = admin.put(
        room['url'], {
            'title': 'thread1', 'body': 'thread1 description',
            'room': False, 'default_rights': None, 'role_id': None,
            'granted_rights': [], 'media': {}})
    assert response.status_code == 200
    thread = response.json()
    # check initial state
    response = admin.get(variation_forum.get_absolute_url())
    assert response.status_code == 200
    data = response.json()
    assert data['rooms'][0]['last_comment']['id']
    assert data['rooms'][0]['comments_count'] == 1
    # delete thread
    response = admin.delete(thread['url'] + '?comment=wow')
    assert response.status_code == 200
    # check counters
    response = admin.get(variation_forum.get_absolute_url())
    assert response.status_code == 200
    data = response.json()
    assert 'last_comment' not in data['rooms'][0]
    assert data['rooms'][0]['comments_count'] == 0
