import pytest

from tulius.forum.threads import models
from tulius.forum.comments import signals


def test_comments_api(client, superuser, admin, user):
    # create root room and thread in it
    response = superuser.put(
        '/api/forum/', {
            'title': 'group', 'body': 'group description',
            'room': True, 'default_rights': None, 'granted_rights': []})
    assert response.status_code == 200
    group = response.json()
    response = admin.put(
        group['url'], {
            'title': 'thread', 'body': 'thread description',
            'room': False, 'default_rights': models.NO_ACCESS,
            'granted_rights': [], 'media': {}})
    assert response.status_code == 200
    thread = response.json()
    assert thread['first_comment_id'] is not None
    # check how thread looks on room page
    response = admin.get(group['url'])
    assert response.status_code == 200
    data = response.json()
    assert data['threads'][0]['comments_count'] == 1
    last_comment = data['threads'][0]['last_comment']
    assert last_comment['id'] == thread['first_comment_id']
    # check comments not readable for other users
    response = user.get(thread['url'] + 'comments_page/')
    assert response.status_code == 403
    # make thread readable
    response = admin.put(
        thread['url'] + 'granted_rights/', {
            'default_rights': models.ACCESS_READ
        })
    assert response.status_code == 200
    # check user now can read comments
    response = user.get(thread['url'] + 'comments_page/')
    assert response.status_code == 200
    data = response.json()
    assert len(data['comments']) == 1
    first_comment = data['comments'][0]
    assert first_comment['title'] == 'thread'
    assert first_comment['body'] == 'thread description'
    assert first_comment['is_thread']
    assert not first_comment['edit_right']
    assert first_comment['id'] == thread['first_comment_id']

    # check that user can't post comments
    response = user.post(
        thread['url'] + 'comments_page/', {
            'reply_id': first_comment['id'],
            'title': 'hello', 'body': 'world',
            'media': {},
        })
    assert response.status_code == 403

    # make thread opened
    response = admin.put(
        thread['url'] + 'granted_rights/', {'default_rights': None})
    assert response.status_code == 200
    # check comment preview works
    response = user.post(
        thread['url'] + 'comments_page/', {
            'reply_id': first_comment['id'],
            'title': 'hello', 'body': 'world',
            'media': {}, 'preview': True,
        })
    assert response.status_code == 200
    data = response.json()
    assert data['id'] is None
    assert data['user']['id'] == user.user.pk
    assert data['title'] == 'hello'
    assert data['body'] == 'world'
    # check that comment really not created
    response = user.get(thread['url'] + 'comments_page/')
    assert response.status_code == 200
    data = response.json()
    assert len(data['comments']) == 1

    # now really post comment
    response = user.post(
        thread['url'] + 'comments_page/', {
            'reply_id': first_comment['id'],
            'title': 'hello', 'body': 'world',
            'media': {},
        })
    assert response.status_code == 200
    data = response.json()
    assert len(data['comments']) == 2
    comment = data['comments'][1]
    assert comment['id']
    assert comment['user']['id'] == user.user.pk
    assert comment['title'] == 'hello'
    assert comment['body'] == 'world'
    # check anonymous cant post comments
    response = client.post(
        thread['url'] + 'comments_page/', {
            'reply_id': first_comment['id'],
            'title': 'hello', 'body': 'world',
            'media': {},
        })
    assert response.status_code == 403
    # check how thread looks on room page
    response = admin.get(group['url'])
    assert response.status_code == 200
    data = response.json()
    assert data['threads'][0]['comments_count'] == 2
    last_comment = data['threads'][0]['last_comment']
    assert last_comment['id'] == comment['id']
    # check user can update his comment
    response = user.post(
        comment['url'], {
            'reply_id': first_comment['id'],
            'title': 'hello world', 'body': 'world is great',
            'media': {},
        })
    assert response.status_code == 200
    data = response.json()
    assert data['id'] == comment['id']
    assert data['title'] == 'hello world'
    assert data['body'] == 'world is great'
    # check it is really updated
    response = user.get(comment['url'])
    assert response.status_code == 200
    data = response.json()
    assert data['id'] == comment['id']
    assert data['title'] == 'hello world'
    assert data['body'] == 'world is great'
    # delete comment
    response = user.delete(comment['url'] + '?comment=wow')
    assert response.status_code == 200
    # check it is deleted
    response = user.get(thread['url'] + 'comments_page/')
    assert response.status_code == 200
    data = response.json()
    assert len(data['comments']) == 1
    assert data['comments'][0]['id'] == first_comment['id']
    # check how thread looks on room page
    response = admin.get(group['url'])
    assert response.status_code == 200
    data = response.json()
    assert data['threads'][0]['comments_count'] == 1
    last_comment = data['threads'][0]['last_comment']
    assert last_comment['id'] == thread['first_comment_id']
    # check we can't delete first comment
    response = superuser.delete(first_comment['url'] + '?comment=wow')
    assert response.status_code == 403
    # add comment by admin
    response = admin.post(
        thread['url'] + 'comments_page/', {
            'reply_id': first_comment['id'],
            'title': 'Im admin', 'body': 'my comment is awesome',
            'media': {},
        })
    assert response.status_code == 200
    data = response.json()
    assert len(data['comments']) == 2
    admin_comment = data['comments'][1]
    # check user can't delete it
    response = user.delete(admin_comment['url'] + '?comment=wow')
    assert response.status_code == 403
    # check user can't update it
    response = user.post(
        admin_comment['url'], {
            'reply_id': first_comment['id'],
            'title': 'hello world', 'body': 'world is great',
            'media': {},
        })
    assert response.status_code == 403
    # check comments readable by anonymous user
    response = client.get(thread['url'] + 'comments_page/')
    assert response.status_code == 200
    data = response.json()
    assert len(data['comments']) == 2
    # check we can't update first comment as comment
    response = admin.post(
        first_comment['url'], {
            'reply_id': first_comment['id'],
            'title': 'hello world', 'body': 'world is great',
            'media': {},
        })
    assert response.status_code == 403
    # check update comment preview
    response = admin.post(
        admin_comment['url'], {
            'reply_id': first_comment['id'],
            'title': 'hello world', 'body': 'world is great',
            'media': {}, 'preview': True
        })
    assert response.status_code == 200
    data = response.json()
    assert data['id'] == admin_comment['id']
    assert data['title'] == 'hello world'
    assert data['body'] == 'world is great'
    # check it is not really updated
    response = admin.get(admin_comment['url'])
    assert response.status_code == 200
    data = response.json()
    assert data['title'] == 'Im admin'
    assert data['body'] == 'my comment is awesome'
    # check we can't reply to comment in other thread
    response = admin.put(
        group['url'], {
            'title': 'thread2', 'body': 'thread2 description',
            'room': False, 'default_rights': None,
            'granted_rights': [], 'media': {}})
    assert response.status_code == 200
    thread2 = response.json()
    response = admin.post(
        thread['url'] + 'comments_page/', {
            'reply_id': thread2['first_comment_id'],
            'title': 'Im admin2', 'body': 'my comment is awesome2',
            'media': {},
        })
    assert response.status_code == 403
    # check comment without body is not added
    response = admin.post(
        thread['url'] + 'comments_page/', {
            'reply_id': thread['first_comment_id'],
            'title': 'Im admin2', 'body': '',
            'media': {},
        })
    assert response.status_code == 200
    data = response.json()
    assert len(data['comments']) == 2


def test_broken_last_comment(room_group, thread, user):
    # check last comment is on place
    response = user.get(room_group['url'])
    assert response.status_code == 200
    data = response.json()
    last_comment = data['threads'][0]['last_comment']
    assert last_comment['id'] == thread['first_comment_id']
    # break it
    obj = models.Thread.objects.get(pk=thread['id'])
    obj.data['last_comment']['all'] += 1
    obj.save()
    # check it not breaks original view
    response = user.get(room_group['url'])
    assert response.status_code == 200
    data = response.json()
    assert 'last_comment' not in data['threads'][0]


def _my_receiver(comment, **_kwargs):
    comment.media['bar'] = 'foo'
    return True


def test_after_update_saves_comment(thread, user):
    # do "fix"
    signals.after_add.connect(_my_receiver)
    try:
        response = user.post(
            thread['url'] + 'comments_page/', {
                'reply_id': thread['first_comment_id'],
                'title': 'ho ho ho', 'body': 'happy new year',
                'media': {},
            })
    finally:
        assert signals.after_add.disconnect(_my_receiver)
    assert response.status_code == 200
    data = response.json()
    response = user.get(data['comments'][1]['url'])
    assert response.status_code == 200
    comment = response.json()
    assert comment['media']['bar'] == 'foo'


def test_comment_counters_on_rights_change(room_group, admin, client):
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
    response = client.get(room_group['url'])
    assert response.status_code == 200
    data = response.json()
    assert data['rooms'][0]['last_comment']['id']
    assert data['rooms'][0]['comments_count'] == 1
    # close thread
    response = admin.put(
        thread['url'] + 'granted_rights/', {
            'default_rights': models.NO_ACCESS})
    assert response.status_code == 200
    # check counters, admin still see
    response = admin.get(room_group['url'])
    assert response.status_code == 200
    data = response.json()
    assert data['rooms'][0]['last_comment']['id']
    assert data['rooms'][0]['comments_count'] == 1
    # but anonymous user is not
    response = client.get(room_group['url'])
    assert response.status_code == 200
    data = response.json()
    assert 'last_comment' not in data['rooms'][0]
    assert data['rooms'][0]['comments_count'] == 0


def test_comment_counters_on_rights_combination(room_group, admin, user):
    # Create room in root room
    response = admin.put(
        room_group['url'], {
            'title': 'room1', 'body': 'room1 description',
            'room': True, 'default_rights': None,
            'granted_rights': []})
    assert response.status_code == 200
    room = response.json()
    # create thread1 - closed
    response = admin.put(
        room['url'], {
            'title': 'thread1', 'body': 'thread1 description',
            'room': False, 'default_rights': models.NO_ACCESS,
            'granted_rights': [], 'media': {}})
    assert response.status_code == 200
    thread1 = response.json()
    # check state
    response = admin.get(room_group['url'])
    assert response.status_code == 200
    data = response.json()
    assert data['rooms'][0]['last_comment']['id'] == \
        thread1['first_comment_id']
    response = user.get(room_group['url'])
    assert response.status_code == 200
    data = response.json()
    assert 'last_comment' not in data['rooms'][0]
    # add opened thread
    response = admin.put(
        room['url'], {
            'title': 'thread2', 'body': 'thread1 description',
            'room': False, 'default_rights': None,
            'granted_rights': [], 'media': {}})
    assert response.status_code == 200
    thread2 = response.json()
    # check it now
    response = admin.get(room_group['url'])
    assert response.status_code == 200
    data = response.json()
    assert data['rooms'][0]['last_comment']['id'] == \
        thread2['first_comment_id']
    assert data['rooms'][0]['comments_count'] == 2
    response = user.get(room_group['url'])
    assert response.status_code == 200
    data = response.json()
    assert data['rooms'][0]['last_comment']['id'] == \
        thread2['first_comment_id']
    assert data['rooms'][0]['comments_count'] == 1
    # grant rights
    response = admin.post(
        thread1['url'] + 'granted_rights/',
        {
            'user': {'id': user.user.pk},
            'access_level': models.ACCESS_READ
        })
    assert response.status_code == 200
    # counters fixed correctly
    response = user.get(room_group['url'])
    assert response.status_code == 200
    data = response.json()
    assert data['rooms'][0]['last_comment']['id'] == \
        thread2['first_comment_id']
    assert data['rooms'][0]['comments_count'] == 2


def test_thread_ordering_by_last_comment(room_group, admin):
    # create thread 1
    response = admin.put(
        room_group['url'], {
            'title': 'thread1', 'body': 'thread1 description',
            'room': False, 'default_rights': None,
            'granted_rights': [], 'media': {}})
    assert response.status_code == 200
    thread1 = response.json()
    # create thread 2
    response = admin.put(
        room_group['url'], {
            'title': 'thread2', 'body': 'thread2 description',
            'room': False, 'default_rights': None,
            'granted_rights': [], 'media': {}})
    assert response.status_code == 200
    thread2 = response.json()
    # check ordering
    response = admin.get(room_group['url'])
    assert response.status_code == 200
    data = response.json()
    assert len(data['threads']) == 2
    assert data['threads'][0]['id'] == thread2['id']
    assert data['threads'][1]['id'] == thread1['id']
    # post comment to thread 1
    response = admin.post(
        thread1['url'] + 'comments_page/', {
            'reply_id': thread1['first_comment_id'],
            'title': 'ho ho ho', 'body': 'happy new year',
            'media': {},
        })
    assert response.status_code == 200
    # check now it goes first
    response = admin.get(room_group['url'])
    assert response.status_code == 200
    data = response.json()
    assert len(data['threads']) == 2
    assert data['threads'][0]['id'] == thread1['id']
    assert data['threads'][1]['id'] == thread2['id']


@pytest.mark.parametrize('default_rights', [models.NO_ACCESS, None])
def test_fix_counters_public_thread_and_empty_room(
        superuser, room_group, user, default_rights):
    # create public thread
    response = superuser.put(
        room_group['url'], {
            'title': 'thread', 'body': 'thread description',
            'room': False, 'default_rights': None, 'important': 'False',
            'granted_rights': [], 'media': {}})
    assert response.status_code == 200
    # create room with no comments
    response = superuser.put(
        room_group['url'], {
            'title': 'room', 'body': 'room description',
            'room': True, 'default_rights': default_rights,
            'granted_rights': [{
                'user': {'id': user.user.pk},
                'access_level': models.ACCESS_READ}]})
    assert response.status_code == 200
    # fix_counters
    response = superuser.post(room_group['url'] + 'fix/')
    assert response.status_code == 200
    data = response.json()
    assert data['result']['threads'] == 3


def test_fix_counters_public_room_in_middle(
        admin, room_group, user, superuser):
    # create public thread
    response = admin.put(
        room_group['url'], {
            'title': 'room', 'body': 'room description',
            'room': True, 'default_rights': None, 'granted_rights': []})
    assert response.status_code == 200
    room = response.json()
    # create public thread
    response = admin.put(
        room['url'], {
            'title': 'thread', 'body': 'thread description',
            'room': False, 'default_rights': models.NO_ACCESS,
            'important': False, 'granted_rights': [], 'media': {}})
    assert response.status_code == 200
    thread = response.json()
    # check counters initial state for simple user
    response = user.get('/api/forum/')
    assert response.status_code == 200
    data = response.json()
    data = {r['id']: r for r in data['groups']}[room_group['id']]
    assert data['rooms'][0]['comments_count'] == 0
    assert 'last_comment' not in data['rooms'][0]
    # check first comment id
    response = user.get(room_group['url'])
    assert response.status_code == 200
    data = response.json()
    assert data['first_comment_id'] is None
    # check counters initial state for admin user
    response = admin.get('/api/forum/')
    assert response.status_code == 200
    data = response.json()
    data = {r['id']: r for r in data['groups']}[room_group['id']]
    assert data['rooms'][0]['comments_count'] == 1
    assert data['rooms'][0]['last_comment']['id'] == thread['first_comment_id']
    # check first comment id
    response = admin.get(room_group['url'])
    assert response.status_code == 200
    data = response.json()
    assert data['first_comment_id'] == thread['first_comment_id']
    # fix_counters
    response = superuser.post(room_group['url'] + 'fix/')
    assert response.status_code == 200
    data = response.json()
    assert data['result']['threads'] == 3
    # check counters for simple user
    response = user.get('/api/forum/')
    assert response.status_code == 200
    data = response.json()
    data = {r['id']: r for r in data['groups']}[room_group['id']]
    assert data['rooms'][0]['comments_count'] == 0
    assert 'last_comment' not in data['rooms'][0]
    # check first comment id
    response = user.get(room_group['url'])
    assert response.status_code == 200
    data = response.json()
    assert data['first_comment_id'] is None
    # check counters for admin
    response = admin.get('/api/forum/')
    assert response.status_code == 200
    data = response.json()
    data = {r['id']: r for r in data['groups']}[room_group['id']]
    assert data['rooms'][0]['comments_count'] == 1
    assert data['rooms'][0]['last_comment']['id'] == thread['first_comment_id']
    # check first comment id
    response = admin.get(room_group['url'])
    assert response.status_code == 200
    data = response.json()
    assert data['first_comment_id'] == thread['first_comment_id']


def test_comments_superuser_counters(superuser, room_group, user):
    # create room with no comments
    response = user.put(
        room_group['url'], {
            'title': 'room', 'body': 'room description',
            'room': True, 'default_rights': None, 'granted_rights': []})
    assert response.status_code == 200
    room = response.json()
    # create hidden thread
    response = user.put(
        room['url'], {
            'title': 'thread', 'body': 'thread description',
            'room': False, 'default_rights': models.NO_ACCESS,
            'important': False, 'granted_rights': [], 'media': {}})
    assert response.status_code == 200
    thread = response.json()
    # check counters by super user
    response = superuser.get(room_group['url'])
    assert response.status_code == 200
    data = response.json()
    assert data['rooms'][0]['comments_count'] == 1
    assert data['rooms'][0]['last_comment']['id'] == thread['first_comment_id']


def test_closed_thread(superuser, room_group):
    # create thread
    response = superuser.put(
        room_group['url'], {
            'title': 'thread', 'body': 'thread description',
            'room': False, 'default_rights': None, 'granted_rights': [],
            'important': True, 'closed': True, 'media': {}})
    assert response.status_code == 200
    thread = response.json()
    assert thread['rights']['write']
    # check add comment
    response = superuser.post(
        thread['url'] + 'comments_page/', {
            'reply_id': thread['first_comment_id'],
            'title': 'ho ho ho', 'body': 'happy new year',
            'media': {},
        })
    assert response.status_code == 200
    # close thread
    thread['closed'] = True
    response = superuser.post(thread['url'], thread)
    assert response.status_code == 200
    thread = response.json()
    assert not thread['rights']['write']
    response = superuser.post(
        thread['url'] + 'comments_page/', {
            'reply_id': thread['first_comment_id'],
            'title': 'ho ho ho', 'body': 'happy new year',
            'media': {},
        })
    assert response.status_code == 403
