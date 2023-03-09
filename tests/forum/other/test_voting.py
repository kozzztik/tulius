import pytest
from django.core import exceptions

from tulius.forum.other import voting


voting_data = {
    'name': 'Vote for <u>best</u> future',
    'body': 'Select <b>your</b> future',
    'show_results': True,
    'preview_results': True,
    'choices': {
        'items': [
            {'name': 'better future'},
            {'name': 'best future'},
            {'name': 'bad future'}
        ]
    }
}

voting_data2 = {
    'name': 'Vote for best future',
    'body': 'Select your future',
    'show_results': False,
    'preview_results': False,
    'choices': {
        'items': [
            {'name': 'best future'},
            {'name': 'bad future'}
        ]
    }
}


def test_voting_create_and_edit_on_thread(room_group, user):
    # preview create thread with voting
    response = user.put(
        room_group['url'], {
            'title': 'thread', 'body': 'thread description',
            'room': False, 'default_rights': None, 'granted_rights': [],
            'preview': True,
            'media': {'voting': voting_data}})
    assert response.status_code == 200
    thread = response.json()
    assert not thread['id']
    assert thread['media']['voting']['name'] == voting_data['name']
    assert thread['media']['voting']['body'] == voting_data['body']
    assert len(thread['media']['voting']['choices']['items']) \
        == len(voting_data['choices']['items'])
    # create thread with voting
    response = user.put(
        room_group['url'], {
            'title': 'thread', 'body': 'thread description',
            'room': False, 'default_rights': None, 'granted_rights': [],
            'media': {'voting': voting_data}})
    assert response.status_code == 200
    thread = response.json()
    voting = thread['media']['voting']
    assert voting['name'] == voting_data['name']
    assert voting['body'] == voting_data['body']
    assert voting['show_results'] == voting_data['show_results']
    assert voting['preview_results'] == voting_data['preview_results']
    assert len(voting['choices']['items']) == 3
    assert voting['choices']['items'][0]['name'] == \
        voting_data['choices']['items'][0]['name']
    assert voting['choices']['items'][1]['name'] == \
        voting_data['choices']['items'][1]['name']
    assert voting['choices']['items'][2]['name'] == \
        voting_data['choices']['items'][2]['name']
    # check how it looks like in comments
    response = user.get(thread['url'] + 'comments_page/')
    assert response.status_code == 200
    data = response.json()
    voting = data['comments'][0]['media']['voting']
    assert voting['name'] == voting_data['name']
    assert voting['body'] == voting_data['body']
    assert voting['show_results'] == voting_data['show_results']
    assert voting['preview_results'] == voting_data['preview_results']
    assert len(voting['choices']['items']) == 3
    assert voting['choices']['items'][0]['name'] == \
        voting_data['choices']['items'][0]['name']
    assert voting['choices']['items'][1]['name'] == \
        voting_data['choices']['items'][1]['name']
    assert voting['choices']['items'][2]['name'] == \
        voting_data['choices']['items'][2]['name']
    # update thread voting preview
    response = user.post(
        thread['url'], {
            'title': 'thread', 'body': 'thread description',
            'preview': True,
            'media': {'voting': voting_data2}})
    assert response.status_code == 200
    data = response.json()
    voting = data['media']['voting']
    assert voting['name'] == voting_data2['name']
    assert voting['body'] == voting_data2['body']
    # important, items not updated
    assert len(voting['choices']['items']) == 3
    assert voting['choices']['items'][0]['name'] == \
        voting_data['choices']['items'][0]['name']
    assert voting['choices']['items'][1]['name'] == \
        voting_data['choices']['items'][1]['name']
    assert voting['choices']['items'][2]['name'] == \
        voting_data['choices']['items'][2]['name']
    # real thread update
    response = user.post(
        thread['url'], {
            'title': 'thread', 'body': 'thread description',
            'media': {'voting': voting_data2}})
    assert response.status_code == 200
    data = response.json()
    voting = data['media']['voting']
    assert voting['name'] == voting_data2['name']
    assert voting['body'] == voting_data2['body']
    assert voting['show_results'] == voting_data2['show_results']
    assert voting['preview_results'] == voting_data2['preview_results']
    # important, items not updated
    assert len(voting['choices']['items']) == 3
    assert voting['choices']['items'][0]['name'] == \
        voting_data['choices']['items'][0]['name']
    assert voting['choices']['items'][1]['name'] == \
        voting_data['choices']['items'][1]['name']
    assert voting['choices']['items'][2]['name'] == \
        voting_data['choices']['items'][2]['name']
    # check how it looks like in comments
    response = user.get(thread['url'] + 'comments_page/')
    assert response.status_code == 200
    data = response.json()
    voting = data['comments'][0]['media']['voting']
    assert voting['name'] == voting_data2['name']
    assert voting['body'] == voting_data2['body']
    assert voting['show_results'] == voting_data2['show_results']
    assert voting['preview_results'] == voting_data2['preview_results']
    # important, items not updated
    assert len(voting['choices']['items']) == 3
    assert voting['choices']['items'][0]['name'] == \
        voting_data['choices']['items'][0]['name']
    assert voting['choices']['items'][1]['name'] == \
        voting_data['choices']['items'][1]['name']
    assert voting['choices']['items'][2]['name'] == \
        voting_data['choices']['items'][2]['name']


def test_add_voting_on_thread(thread, admin):
    # update thread voting preview
    response = admin.post(
        thread['url'], {
            'title': 'thread', 'body': 'thread description',
            'preview': True,
            'media': {'voting': voting_data}})
    assert response.status_code == 200
    data = response.json()
    assert data['media']['voting']['name'] == voting_data['name']
    assert data['media']['voting']['body'] == voting_data['body']
    assert len(data['media']['voting']['choices']['items']) \
        == len(voting_data['choices']['items'])
    # do real add
    response = admin.post(
        thread['url'], {
            'title': 'thread', 'body': 'thread description',
            'media': {'voting': voting_data}})
    assert response.status_code == 200
    data = response.json()
    voting = data['media']['voting']
    assert voting['name'] == voting_data['name']
    assert voting['body'] == voting_data['body']
    assert voting['show_results'] == voting_data['show_results']
    assert voting['preview_results'] == voting_data['preview_results']
    assert len(voting['choices']['items']) == 3
    assert voting['choices']['items'][0]['name'] == \
        voting_data['choices']['items'][0]['name']
    assert voting['choices']['items'][1]['name'] == \
        voting_data['choices']['items'][1]['name']
    assert voting['choices']['items'][2]['name'] == \
        voting_data['choices']['items'][2]['name']


def test_voting_create_and_edit_on_comment(thread, user, client):
    # preview create comment with voting
    response = user.post(
        thread['url'] + 'comments_page/', {
            'reply_id': thread['first_comment_id'],
            'title': 'foo', 'body': 'bar', 'preview': True,
            'media': {'voting': voting_data},
        })
    assert response.status_code == 200
    data = response.json()
    assert data['id'] is None
    assert data['media']['voting']['name'] == voting_data['name']
    assert data['media']['voting']['body'] == voting_data['body']
    assert len(data['media']['voting']['choices']['items']) \
        == len(voting_data['choices']['items'])
    # create comment with voting
    response = user.post(
        thread['url'] + 'comments_page/', {
            'reply_id': thread['first_comment_id'],
            'title': 'thread', 'body': 'thread description',
            'media': {'voting': voting_data}})
    assert response.status_code == 200
    data = response.json()
    assert len(data['comments']) == 2
    comment = data['comments'][1]
    voting = comment['media']['voting']
    assert voting['name'] == voting_data['name']
    assert voting['body'] == voting_data['body']
    assert voting['show_results'] == voting_data['show_results']
    assert voting['preview_results'] == voting_data['preview_results']
    assert len(voting['choices']['items']) == 3
    assert voting['choices']['items'][0]['name'] == \
        voting_data['choices']['items'][0]['name']
    assert voting['choices']['items'][1]['name'] == \
        voting_data['choices']['items'][1]['name']
    assert voting['choices']['items'][2]['name'] == \
        voting_data['choices']['items'][2]['name']
    # check it is not broken for anonymous client
    response = client.get(comment['url'])
    assert response.status_code == 200
    data = response.json()
    assert data['media']['voting'] == voting
    # update comment voting preview
    response = user.post(
        comment['url'], {
            'title': 'thread', 'body': 'thread description',
            'preview': True,
            'media': {'voting': voting_data2}})
    assert response.status_code == 200
    data = response.json()
    assert data['media']['voting']['name'] == voting_data2['name']
    assert data['media']['voting']['body'] == voting_data2['body']
    assert len(data['media']['voting']['choices']['items']) \
        == len(voting_data['choices']['items'])
    # real comment update
    response = user.post(
        comment['url'], {
            'title': 'thread', 'body': 'thread description',
            'media': {'voting': voting_data2}})
    assert response.status_code == 200
    data = response.json()
    voting = data['media']['voting']
    assert voting['name'] == voting_data2['name']
    assert voting['body'] == voting_data2['body']
    assert voting['show_results'] == voting_data2['show_results']
    assert voting['preview_results'] == voting_data2['preview_results']
    # important, items not updated
    assert len(voting['choices']['items']) == 3
    assert voting['choices']['items'][0]['name'] == \
        voting_data['choices']['items'][0]['name']
    assert voting['choices']['items'][1]['name'] == \
        voting_data['choices']['items'][1]['name']
    assert voting['choices']['items'][2]['name'] == \
        voting_data['choices']['items'][2]['name']


def test_add_voting_on_comment(thread, user):
    # create comment without voting
    response = user.post(
        thread['url'] + 'comments_page/', {
            'reply_id': thread['first_comment_id'],
            'title': 'thread', 'body': 'thread description',
            'media': {}})
    assert response.status_code == 200
    data = response.json()
    assert len(data['comments']) == 2
    comment = data['comments'][1]
    # update comment voting preview
    response = user.post(
        comment['url'], {
            'title': 'thread', 'body': 'thread description',
            'preview': True,
            'media': {'voting': voting_data}})
    assert response.status_code == 200
    data = response.json()
    assert data['media']['voting']['name'] == voting_data['name']
    assert data['media']['voting']['body'] == voting_data['body']
    assert len(data['media']['voting']['choices']['items']) \
        == len(voting_data['choices']['items'])
    # do real add
    response = user.post(
        comment['url'], {
            'title': 'thread', 'body': 'thread description',
            'media': {'voting': voting_data}})
    assert response.status_code == 200
    data = response.json()
    voting = data['media']['voting']
    assert voting['name'] == voting_data['name']
    assert voting['body'] == voting_data['body']
    assert voting['show_results'] == voting_data['show_results']
    assert voting['preview_results'] == voting_data['preview_results']
    assert len(voting['choices']['items']) == 3
    assert voting['choices']['items'][0]['name'] == \
        voting_data['choices']['items'][0]['name']
    assert voting['choices']['items'][1]['name'] == \
        voting_data['choices']['items'][1]['name']
    assert voting['choices']['items'][2]['name'] == \
        voting_data['choices']['items'][2]['name']


@pytest.mark.parametrize('preview_results', [True, False])
@pytest.mark.parametrize('show_results', [True, False])
def test_voting_process(
        thread, admin, user, superuser, show_results, preview_results):
    voting = voting_data.copy()
    voting['show_results'] = show_results
    voting['preview_results'] = preview_results
    # create comment with voting
    response = user.post(
        thread['url'] + 'comments_page/', {
            'reply_id': thread['first_comment_id'],
            'title': 'thread', 'body': 'thread description',
            'media': {'voting': voting}})
    assert response.status_code == 200
    data = response.json()
    assert len(data['comments']) == 2
    comment = data['comments'][1]
    voting = comment['media']['voting']
    assert voting['show_results'] == show_results
    assert voting['preview_results'] == preview_results
    assert voting['choices']['votes'] == 0
    for item in voting['choices']['items']:
        if preview_results:
            assert item['count'] == 0
            assert item['percent'] == 0
        else:
            assert item['count'] is None
            assert 'percent' not in item
    # check voting get API
    response = user.get(data['comments'][0]['url'] + 'voting/')
    assert response.status_code == 404
    response = user.get(comment['url'] + 'voting/')
    assert response.status_code == 200
    data = response.json()
    assert data['name'] == voting['name']
    assert data['body'] == voting['body']
    assert len(data['choices']['items']) == len(voting['choices']['items'])
    # vote by other user
    response = admin.post(
        comment['url'] + 'voting/',
        {'choice': voting['choices']['items'][0]['id']})
    assert response.status_code == 200
    data = response.json()
    if show_results or preview_results:
        assert data['choices']['items'][0]['count'] == 1
        assert data['choices']['items'][0]['percent'] == 100.0
        assert data['choices']['items'][1]['count'] == 0
        assert data['choices']['items'][1]['percent'] == 0.0
    else:
        assert data['choices']['items'][0]['count'] is None
        assert 'percent' not in data['choices']['items'][0]
    assert data['choices']['votes'] == 1
    # vote by user itself
    response = user.post(
        comment['url'] + 'voting/',
        {'choice': voting['choices']['items'][1]['id']})
    assert response.status_code == 200
    data = response.json()
    if show_results or preview_results:
        assert data['choices']['items'][0]['count'] == 1
        assert data['choices']['items'][0]['percent'] == 50.0
        assert data['choices']['items'][1]['count'] == 1
        assert data['choices']['items'][1]['percent'] == 50.0
    else:
        assert data['choices']['items'][0]['count'] is None
        assert 'percent' not in data['choices']['items'][0]
    assert data['choices']['votes'] == 2
    # try to revote
    response = user.post(
        comment['url'] + 'voting/',
        {'choice': voting['choices']['items'][0]['id']})
    assert response.status_code == 404
    # check other user cant close voting
    response = admin.post(comment['url'] + 'voting/', {'close': True})
    assert response.status_code == 403
    # close voting
    response = user.post(comment['url'] + 'voting/', {'close': True})
    assert response.status_code == 200
    data = response.json()
    assert data['choices']['items'][0]['count'] == 1
    assert data['choices']['items'][0]['percent'] == 50.0
    assert data['choices']['items'][1]['count'] == 1
    assert data['choices']['items'][1]['percent'] == 50.0
    assert data['choices']['votes'] == 2


def test_vote_with_wrong_id(thread, user):
    # create first comment with voting
    response = user.post(
        thread['url'] + 'comments_page/', {
            'reply_id': thread['first_comment_id'],
            'title': 'thread', 'body': 'thread description',
            'media': {'voting': voting_data}})
    assert response.status_code == 200
    data = response.json()
    assert len(data['comments']) == 2
    comment = data['comments'][1]
    voting = comment['media']['voting']
    # try to vote with wrong id
    with pytest.raises(exceptions.ValidationError):
        response = user.post(
            comment['url'] + 'voting/',
            {'choice': voting['choices']['items'][0]['id'] + 100})
        assert response.status_code == 404


def test_broken_voting(room_group, user):
    data = {
        'body': 'some body',
        'choice': None,
        'choices': {
            'items': [
                {"count": None, "id": 0, "name": 'option 1'},
                {"count": None, "id": 1, "name": 'option 2'}
            ],
            'votes': 7,
            'with_results': False
        },
        'closed': False,
        'id': 3446262,
        'name': 'some name',
        'preview_results': False,
        'show_results': True,
    }
    voting.VotingAPI.user_voting_data(data, user.user, 0)
