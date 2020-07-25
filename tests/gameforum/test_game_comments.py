from django.db import transaction

from tulius.forum.threads import models as forum_threads
from tulius.forum.rights import models as rights
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
        base_url + f'thread/{variation_forum.id}/', {
            'title': 'thread', 'body': 'thread description',
            'room': False,
            'access_type': forum_threads.THREAD_ACCESS_TYPE_NO_WRITE,
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
            'access_level': rights.THREAD_ACCESS_WRITE
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
            'access_type': forum_threads.THREAD_ACCESS_TYPE_NOT_SET,
            'granted_rights': [], 'role_id': detective.pk, 'media': {
                'illustrations': [{
                    'id' : story_illustration.pk,
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
            'access_type': forum_threads.THREAD_ACCESS_TYPE_NOT_SET,
            'granted_rights': [], 'role_id': detective.pk, 'media': {}
        })
    assert response.status_code == 200
    thread = response.json()
    # break last comment
    obj = thread_models.Thread.objects.get(pk=thread['id'])
    obj.last_comment_id += 1
    obj.save()
    # check room view still works
    response = user.get(base_url + f'thread/{variation_forum.id}/')
    assert response.status_code == 200
    data = response.json()
    assert 'last_comment' not in data['threads'][0]
