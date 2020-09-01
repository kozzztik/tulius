from unittest import mock

from django.utils import timezone

from tulius.forum.threads import models as thread_models
from tulius.forum.comments import models


def test_options(user, room_group):
    response = user.options(
        f'/api/forum/thread/{room_group["id"]}/search/?query=Tul')
    assert response.status_code == 200
    data = response.json()
    for u in data['users']:
        assert 'Tul' in u['title']


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
        f'/api/forum/thread/{thread["id"]}/search/',
        {'users': [admin.user.pk]})
    assert response.status_code == 200
    data = response.json()
    assert len(data['results']) == 2
    for result in data['results']:
        assert result['comment']['user']['id'] == admin.user.id
    # do search for not user
    response = user.post(
        f'/api/forum/thread/{thread["id"]}/search/',
        {'not_users': [admin.user.pk]})
    assert response.status_code == 200
    data = response.json()
    assert len(data['results']) == 1
    comment = data['results'][0]['comment']
    assert comment['user']['id'] == user.user.id
    # do search by text
    response = user.post(
        f'/api/forum/thread/{thread["id"]}/search/',
        {'text': 'foo'})
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
        f'/api/forum/thread/{thread["id"]}/search/',
        {'date_to': '10.10.2019'})
    assert response.status_code == 200
    data = response.json()
    assert len(data['results']) == 1
    assert data['results'][0]['comment']['id'] == comment1.pk
    # do combined time search
    response = user.post(
        f'/api/forum/thread/{thread["id"]}/search/',
        {'date_from': '10.10.2019', 'date_to': '02.02.2020'})
    assert response.status_code == 200
    data = response.json()
    assert len(data['results']) == 1
    assert data['results'][0]['comment']['id'] == comment2.pk
    # do search with incorrect date
    response = user.post(
        f'/api/forum/thread/{thread["id"]}/search/',
        {'date_to': '10.10.2019', 'date_from': 'foobar'})
    assert response.status_code == 200
    data = response.json()
    assert len(data['results']) == 1
    assert data['results'][0]['comment']['id'] == comment1.pk


def test_too_much_results(thread, user):
    response = user.post(
        thread['url'] + 'comments_page/', {
            'reply_id': thread['first_comment_id'],
            'title': 'title', 'body': 'Some text',
            'media': {},
        })
    assert response.status_code == 200
    comment = models.Comment.objects.filter(parent_id=thread['id'])[1]
    # do search for user faking search results
    query = mock.MagicMock()
    query.filter.return_value = [comment] * 55
    with mock.patch.object(
            models.Comment.objects, 'select_related',
            return_value=query) as mock_method:
        response = user.post(
            f'/api/forum/thread/{thread["id"]}/search/',
            {})
        assert mock_method.called
        assert query.filter.called
    assert response.status_code == 200
    data = response.json()
    assert len(data['results']) == 50


def test_search_access_rights(room_group, thread, admin, user):
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
    response = admin.post(f'/api/forum/thread/{room_group["id"]}/search/', {})
    assert response.status_code == 200
    data = response.json()
    assert len(data['results']) == 2
    # search by user in room
    response = user.post(f'/api/forum/thread/{room_group["id"]}/search/', {})
    assert response.status_code == 200
    data = response.json()
    assert len(data['results']) == 1
    # delete thread
    response = admin.delete(thread['url'] + '?comment=wow')
    assert response.status_code == 200
    # check deleted comments filtered
    response = admin.post(f'/api/forum/thread/{room_group["id"]}/search/', {})
    assert response.status_code == 200
    data = response.json()
    assert len(data['results']) == 1
