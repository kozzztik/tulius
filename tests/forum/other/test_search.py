import logging
import time
from unittest import mock

from django.db.models import signals
from django.conf import settings
from django.utils import timezone
import pytest
from elasticsearch7 import exceptions

from tulius.forum.threads import models as thread_models
from tulius.forum.comments import models
from tulius.forum.elastic_search import models as es_models
from tulius.forum.elastic_search import tasks


def setup_module(module):
    signals.post_save.connect(es_models.do_direct_index, sender=models.Comment)


def teardown_module(module):
    """ teardown any state that was previously setup with a setup_module
    method.
    """
    assert signals.post_save.disconnect(
        es_models.do_direct_index, sender=models.Comment)


def test_options(user, superuser):
    response = user.options('/api/forum/search/?query=Tul')
    assert response.status_code == 200
    data = response.json()
    for u in data['users']:
        assert 'Tul' in u['title']
    pks = f'{user.user.pk},{superuser.user.pk}'
    response = user.options(f'/api/forum/search/?pks={pks}')
    assert response.status_code == 200
    data = response.json()
    assert len(data['users']) == 2
    users = {u['id']: u for u in data['users']}
    assert users[user.user.pk]['title'] == user.user.username
    assert users[superuser.user.pk]['title'] == superuser.user.username


def test_search_conditions(admin, user, thread):
    response = admin.post(
        thread['url'] + 'comments_page/', {
            'reply_id': thread['first_comment_id'],
            'title': 'title', 'body': 'Some foo text',
            'media': {},
        })
    assert response.status_code == 200
    response = user.post(
        thread['url'] + 'comments_page/', {
            'reply_id': thread['first_comment_id'],
            'title': 'title', 'body': 'Some bar text',
            'media': {},
        })
    assert response.status_code == 200
    # do search for user
    response = user.post(
        '/api/forum/search/',
        {'users': [admin.user.pk], 'thread_id': thread["id"]})
    assert response.status_code == 200
    data = response.json()
    assert len(data['results']) == 2
    for result in data['results']:
        assert result['comment']['user']['id'] == admin.user.id
    # do search for not user
    response = user.post(
        '/api/forum/search/',
        {'not_users': [admin.user.pk], 'thread_id': thread["id"]})
    assert response.status_code == 200
    data = response.json()
    assert len(data['results']) == 1
    comment = data['results'][0]['comment']
    assert comment['user']['id'] == user.user.id
    # do search by text
    response = user.post(
        '/api/forum/search/',
        {'text': 'foo', 'thread_id': thread["id"]})
    assert response.status_code == 200
    data = response.json()
    assert len(data['results']) == 1
    comment = data['results'][0]['comment']
    assert 'foo' in comment['body']
    # create conditions for data search
    comments = models.Comment.objects.filter(parent_id=thread['id'])
    tz = timezone.get_default_timezone()
    comment1 = comments[1]
    comment1.create_time = timezone.datetime(
        2019, 1, 1, 0, 0, 0, 0, tzinfo=tz)
    comment1.save()
    comment2 = comments[2]
    comment2.create_time = timezone.datetime(
        2020, 1, 1, 0, 0, 0, 0, tzinfo=tz)
    comment2.save()
    # do search "before"
    response = user.post(
        '/api/forum/search/',
        {'date_to': '2019-10-10', 'thread_id': thread["id"]})
    assert response.status_code == 200
    data = response.json()
    assert len(data['results']) == 1
    assert data['results'][0]['comment']['id'] == comment1.pk
    # do combined time search
    response = user.post(
        '/api/forum/search/', {
            'date_from': '2019-10-10',
            'date_to': '2020-02-02',
            'thread_id': thread["id"]
        })
    assert response.status_code == 200
    data = response.json()
    assert len(data['results']) == 1
    assert data['results'][0]['comment']['id'] == comment2.pk
    # do search with incorrect date
    response = user.post(
        '/api/forum/search/', {
            'date_to': '2019-10-10',
            'date_from': 'foobar',
            'thread_id': thread["id"]
        })
    assert response.status_code == 200
    data = response.json()
    assert len(data['results']) == 1
    assert data['results'][0]['comment']['id'] == comment1.pk


def test_search_access_rights(room_group, thread, admin, user, superuser):
    # create thread with limited access
    response = admin.put(
        room_group['url'], {
            'title': 'thread', 'body': 'thread description',
            'room': False,
            'default_rights': thread_models.NO_ACCESS,
            'granted_rights': [],
            'important': False, 'media': {}})
    assert response.status_code == 200
    # search by admin in room
    response = admin.post(
        '/api/forum/search/', {'thread_id': room_group["id"]})
    assert response.status_code == 200
    data = response.json()
    assert len(data['results']) == 2
    # search by user in room
    response = user.post('/api/forum/search/', {'thread_id': room_group["id"]})
    assert response.status_code == 200
    data = response.json()
    assert len(data['results']) == 1
    # search by superuser in room
    response = superuser.post(
        '/api/forum/search/', {'thread_id': room_group["id"]})
    assert response.status_code == 200
    data = response.json()
    assert len(data['results']) == 2
    # delete thread
    response = admin.delete(thread['url'] + '?comment=wow')
    assert response.status_code == 200
    # check deleted comments filtered
    response = admin.post(
        '/api/forum/search/', {'thread_id': room_group["id"]})
    assert response.status_code == 200
    data = response.json()
    assert len(data['results']) == 1


def test_search_access_rights_double_check(
        room_group, thread, admin, user, superuser):
    # check initial state
    response = user.post('/api/forum/search/', {'thread_id': room_group["id"]})
    assert response.status_code == 200
    data = response.json()
    assert len(data['results']) == 1
    # silently close thread with no reindex.
    thread = thread_models.Thread.objects.get(pk=thread['id'])
    thread.rights.all = 0
    count = thread_models.Thread.objects.filter(pk=thread.pk).update(
        data=thread.data)
    assert count == 1
    # search by superuser in room again
    response = user.post('/api/forum/search/', {'thread_id': room_group["id"]})
    assert response.status_code == 200
    data = response.json()
    assert len(data['results']) == 0


def test_reindex_all(superuser, admin):
    # break indexed user
    old_value = admin.user.animation_speed
    admin.user.animation_speed = old_value + 100
    try:
        es_models.do_direct_index(admin.user)
        # check it is now broken
        doc = es_models.client.get(
            es_models.index_name(admin.user.__class__), admin.user.pk)
        assert doc['_source']['animation_speed'] == old_value + 100
        # try reindex by not superuser
        response = admin.post('/api/forum/elastic/reindex/all/')
        assert response.status_code == 403
        # do reindex all (but only users)
        with mock.patch.object(
                settings, 'ELASTIC_MODELS', (('tulius', 'User'),)):
            response = superuser.post('/api/forum/elastic/reindex/all/')
        assert response.status_code == 200
        # check user is fixed
        doc = es_models.client.get(
            es_models.index_name(admin.user.__class__), admin.user.pk)
        assert doc['_source']['animation_speed'] == old_value
    finally:
        admin.user.animation_speed = old_value


def test_index_restore(superuser, admin):
    es_models.client.indices.delete(es_models.index_name(admin.user.__class__))
    # check it is now broken
    with pytest.raises(exceptions.NotFoundError):
        es_models.client.get(
            es_models.index_name(admin.user.__class__), admin.user.pk)
    # do reindex all (but only users)
    with mock.patch.object(settings, 'ELASTIC_MODELS', (('tulius', 'User'),)):
        response = superuser.post('/api/forum/elastic/reindex/all/')
    assert response.status_code == 200
    # check user is fixed
    doc = es_models.client.get(
        es_models.index_name(admin.user.__class__), admin.user.pk)
    assert doc['_source']['animation_speed'] == admin.user.animation_speed


def test_reindex_room(superuser, admin, room_group, thread):
    comment = models.Comment.objects.get(pk=thread['first_comment_id'])
    # break indexed thread
    old_value = comment.title
    comment.title = old_value + 'foobar'
    es_models.do_direct_index(comment)
    # flush index to be sure get will return fresh data
    es_models.client.indices.flush(es_models.index_name(models.Comment))
    # check it is now broken
    # some workaround about index refresh. Sometime it needs some time for
    # document to appear in index and flush not helps
    for i in range(3):
        if i:
            time.sleep(2)
        doc = es_models.client.get(
            es_models.index_name(comment.__class__), comment.pk)
        if doc['_source']['title'] == old_value + 'foobar':
            break
    assert doc['_source']['title'] == old_value + 'foobar'
    # try reindex by not superuser
    response = admin.post(
        f'/api/forum/elastic/reindex/thread/{room_group["id"]}/')
    assert response.status_code == 403
    # do reindex all (but only users)
    response = superuser.post(
        f'/api/forum/elastic/reindex/thread/{room_group["id"]}/')
    assert response.status_code == 200
    # check user is fixed
    doc = es_models.client.get(
        es_models.index_name(comment.__class__), comment.pk)
    assert doc['_source']['title'] == old_value


def test_reindex_room_bulk_reported(superuser, room_group, thread):
    # create comment to make second bulk
    response = superuser.post(
        thread['url'] + 'comments_page/', {
            'reply_id': thread['first_comment_id'],
            'title': 'hello', 'body': 'world',
            'media': {},
        })
    assert response.status_code == 200
    # mock all
    bulk = mock.MagicMock()
    bulk.return_value = {'errors': False}
    progress = mock.MagicMock()
    url = f'/api/forum/elastic/reindex/thread/{room_group["id"]}/'
    with mock.patch.object(tasks.ReindexComments, 'bulk_size', 1):
        with mock.patch.object(tasks.ReindexComments, 'counter_chunk', 1):
            with mock.patch.object(
                    tasks.ReindexComments, 'progress', progress):
                with mock.patch.object(es_models.client, 'bulk', bulk):
                    response = superuser.post(url)
    assert response.status_code == 200
    # check calls
    assert bulk.call_count == 2
    assert progress.call_count == 4


def test_reindex_room_bulk_failed(superuser, room_group, thread):
    # mock all
    logger = logging.getLogger('celery.task')
    bulk = mock.MagicMock()
    bulk.return_value = {'errors': True}
    exc = mock.MagicMock()
    url = f'/api/forum/elastic/reindex/thread/{room_group["id"]}/'
    with mock.patch.object(logger, 'exception', exc):
        with mock.patch.object(es_models.client, 'bulk', bulk):
            response = superuser.post(url)
    assert response.status_code == 200
    # check calls
    assert bulk.call_count == 1
    assert exc.call_count == 1


def test_search_after_move(superuser, room_group):
    # create root target room
    response = superuser.put(
        room_group['url'], {
            'title': 'target', 'body': 'target description',
            'room': True, 'default_rights': None,
            'granted_rights': []})
    assert response.status_code == 200
    target = response.json()
    # create source for move
    response = superuser.put(
        room_group['url'], {
            'title': 'source', 'body': 'source description',
            'room': True, 'default_rights': None,
            'granted_rights': []})
    assert response.status_code == 200
    source = response.json()
    # create thread
    response = superuser.put(
        source['url'], {
            'title': 'thread', 'body': 'thread description',
            'room': False, 'default_rights': None,
            'granted_rights': [], 'media': {}})
    assert response.status_code == 200
    thread = response.json()
    # check initial state
    response = superuser.post(
        '/api/forum/search/', {'thread_id': source['id']})
    assert response.status_code == 200
    data = response.json()
    assert data['results'][0]['thread']['id'] == thread['id']
    response = superuser.post(
        '/api/forum/search/', {'thread_id': target['id']})
    assert response.status_code == 200
    data = response.json()
    assert not data['results']
    # do move
    response = superuser.put(
        thread['url'] + 'move/', {'parent_id': target['id']})
    assert response.status_code == 200
    # check search results
    response = superuser.post(
        '/api/forum/search/', {'thread_id': source['id']})
    assert response.status_code == 200
    data = response.json()
    assert not data['results']
    response = superuser.post(
        '/api/forum/search/', {'thread_id': target['id']})
    assert response.status_code == 200
    data = response.json()
    assert data['results'][0]['thread']['id'] == thread['id']
