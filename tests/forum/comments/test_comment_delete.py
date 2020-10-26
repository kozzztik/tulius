from unittest import mock

from tulius.forum.comments import models


def test_delete_comments_pagination(room_group, thread, user):
    with mock.patch.object(models.Comment, 'COMMENTS_ON_PAGE', 1):
        # post first comment
        response = user.post(
            thread['url'] + 'comments_page/', {
                'reply_id': thread['first_comment_id'],
                'title': 'hello', 'body': 'comment1', 'media': {}})
        assert response.status_code == 200
        data = response.json()
        assert len(data['comments']) == 1
        comment1 = data['comments'][0]
        assert comment1['page'] == 2
        # post second comment
        response = user.post(
            thread['url'] + 'comments_page/', {
                'reply_id': thread['first_comment_id'],
                'title': 'hello', 'body': 'comment2', 'media': {}})
        assert response.status_code == 200
        data = response.json()
        assert len(data['comments']) == 1
        comment2 = data['comments'][0]
        assert comment2['page'] == 3
        # check comment2 is on 3 page
        response = user.get(thread['url'] + 'comments_page/?page=3')
        assert response.status_code == 200
        data = response.json()
        assert len(data['comments']) == 1
        assert data['comments'][0]['id'] == comment2['id']
    # delete first comment
    with mock.patch.object(models.Comment, 'COMMENTS_ON_PAGE', 1):
        response = user.delete(comment1['url'] + '?comment=wow')
        assert response.status_code == 200
        # check second comment now on page 2
        response = user.get(thread['url'] + 'comments_page/?page=2')
    assert response.status_code == 200
    data = response.json()
    assert len(data['comments']) == 1
    assert data['comments'][0]['id'] == comment2['id']


def test_comment_delete_mutation(room_group, thread, superuser):
    response = superuser.delete(room_group['url'] + '?comment=wow')
    assert response.status_code == 200
    obj = models.Comment.objects.get(pk=thread['first_comment_id'])
    assert obj.deleted
    assert obj.parent.deleted


def test_comment_counters_on_thread_delete(room_group, admin):
    # Create room in root room
    response = admin.put(
        room_group['url'], {
            'title': 'room1', 'body': 'room1 description',
            'room': True, 'default_rights': None,
            'granted_rights': []})
    assert response.status_code == 200
    room = response.json()
    # create thread
    response = admin.put(
        room['url'], {
            'title': 'thread1', 'body': 'thread1 description',
            'room': False, 'default_rights': None,
            'granted_rights': [], 'media': {}})
    assert response.status_code == 200
    thread = response.json()
    # check initial state
    response = admin.get(room_group['url'])
    assert response.status_code == 200
    data = response.json()
    assert data['rooms'][0]['last_comment']['id']
    assert data['rooms'][0]['comments_count'] == 1
    # delete thread
    response = admin.delete(thread['url'] + '?comment=wow')
    assert response.status_code == 200
    # check counters
    response = admin.get(room_group['url'])
    assert response.status_code == 200
    data = response.json()
    assert 'last_comment' not in data['rooms'][0]
    assert data['rooms'][0]['comments_count'] == 0
