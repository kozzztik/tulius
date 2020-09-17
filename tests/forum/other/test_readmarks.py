from tulius.forum.threads import models


def test_read_marks(room_group, admin, user):
    # create a "real" room in group
    response = admin.put(
        room_group['url'], {
            'title': 'group1', 'body': 'group1 description',
            'room': True, 'default_rights': None, 'granted_rights': []})
    assert response.status_code == 200
    room = response.json()
    # make a thread for room
    response = admin.put(
        room['url'], {
            'title': 'thread', 'body': 'thread description',
            'room': False, 'default_rights': None, 'granted_rights': [],
            'important': False, 'media': {}})
    assert response.status_code == 200
    thread = response.json()
    # post a comment to thread
    response = admin.post(
        thread['url'] + 'comments_page/', {
            'reply_id': thread['first_comment_id'],
            'title': 'foo', 'body': 'bar',
            'media': {'html': '<textarea></textarea>'},
        })
    assert response.status_code == 200
    data = response.json()
    assert len(data['comments']) == 2
    comment = data['comments'][1]
    # check how it looks like on index
    response = user.get('/api/forum/')
    assert response.status_code == 200
    data = response.json()
    rooms = {g['id']: g for g in data['groups']}
    room_data = rooms[room_group['id']]
    assert room_data['not_read']['id'] == thread['first_comment_id']
    # check how it looks for admin
    response = admin.get('/api/forum/')
    assert response.status_code == 200
    data = response.json()
    rooms = {g['id']: g for g in data['groups']}
    room_data = rooms[room_group['id']]
    assert room_data['not_read'] is None
    # mark first comment as read
    response = user.post(
        thread['url'] + 'read_mark/',
        {'comment_id': thread['first_comment_id']})
    assert response.status_code == 200
    data = response.json()
    assert data['last_read_id'] == thread['first_comment_id']
    assert data['not_read']['id'] == comment['id']
    assert data['not_read']['count'] == 1
    # check how it looks like on index
    response = user.get('/api/forum/')
    assert response.status_code == 200
    data = response.json()
    rooms = {g['id']: g for g in data['groups']}
    room_data = rooms[room_group['id']]
    assert room_data['not_read']['id'] == comment['id']
    # check how it looks on room
    response = user.get(room['url'])
    assert response.status_code == 200
    data = response.json()
    assert data['threads'][0]['not_read']['id'] == comment['id']
    # check how it looks on thread
    response = user.get(thread['url'])
    assert response.status_code == 200
    data = response.json()
    assert data['not_read']['id'] == comment['id']
    assert data['not_read']['count'] == 1
    # now mark all forum as read
    response = user.post('/api/forum/read_mark/', {'comment_id': None})
    assert response.status_code == 200
    data = response.json()
    assert data['last_read_id'] is None
    assert data['not_read'] is None
    # check index
    response = user.get('/api/forum/')
    assert response.status_code == 200
    data = response.json()
    rooms = {g['id']: g for g in data['groups']}
    room_data = rooms[room_group['id']]
    assert room_data['not_read'] is None
    # check room
    response = user.get(room['url'])
    assert response.status_code == 200
    data = response.json()
    assert data['threads'][0]['not_read'] is None
    # check thread
    response = user.get(thread['url'])
    assert response.status_code == 200
    data = response.json()
    assert data['not_read'] is None
    # Delete readmark
    response = user.delete(thread['url'] + 'read_mark/')
    assert response.status_code == 200
    data = response.json()
    assert data['last_read_id'] is None
    assert data['not_read']['id'] == thread['first_comment_id']
    assert data['not_read']['count'] == 2
    # check room
    response = user.get(room['url'])
    assert response.status_code == 200
    data = response.json()
    assert data['threads'][0]['not_read']['id'] == thread['first_comment_id']


def test_readmark_rights(room_group, admin, user):
    # create a "real" room in group
    response = admin.put(
        room_group['url'], {
            'title': 'group1', 'body': 'group1 description',
            'room': True, 'default_rights': None, 'granted_rights': []})
    assert response.status_code == 200
    room = response.json()
    # make a thread for room
    response = admin.put(
        room['url'], {
            'title': 'thread', 'body': 'thread description',
            'room': False, 'default_rights': models.NO_ACCESS,
            'granted_rights': [], 'important': False, 'media': {}})
    assert response.status_code == 200
    thread = response.json()
    # try to put readmark on thread with no access
    response = user.post(
        thread['url'] + 'read_mark/',
        {'comment_id': thread['first_comment_id']})
    assert response.status_code == 403
    # mark all as read
    response = user.post('/api/forum/read_mark/', {'comment_id': None})
    assert response.status_code == 200
    data = response.json()
    assert data['last_read_id'] is None
    assert data['not_read'] is None
    # open thread
    response = admin.put(
        thread['url'] + 'granted_rights/', {'default_rights': None})
    assert response.status_code == 200
    # check how it looks now on index
    response = user.get('/api/forum/')
    assert response.status_code == 200
    data = response.json()
    rooms = {g['id']: g for g in data['groups']}
    room_data = rooms[room_group['id']]
    assert room_data['not_read']['id'] == thread['first_comment_id']


def test_thread_author_notified(room_group, thread, admin, user):
    response = user.post(
        thread['url'] + 'comments_page/', {
            'reply_id': thread['first_comment_id'],
            'title': 'hello', 'body': 'world',
            'media': {},
        })
    assert response.status_code == 200
    data = response.json()
    comment = data['comments'][1]
    # check on room
    response = admin.get(room_group['url'])
    assert response.status_code == 200
    room = response.json()
    assert room['threads'][0]['not_read']['id'] == comment['id']
    # delete user comment
    response = user.delete(comment['url'] + '?comment=foo')
    assert response.status_code == 200
    # check on room
    response = admin.get(room_group['url'])
    assert response.status_code == 200
    room = response.json()
    assert room['threads'][0]['not_read'] is None


def test_deleted_threads_not_marked(room_group, admin, superuser):
    # make a room
    response = admin.put(
        room_group['url'], {
            'title': 'room', 'body': 'room description',
            'room': True, 'default_rights': None,
            'granted_rights': []})
    assert response.status_code == 200
    room = response.json()
    # make a first thread
    response = admin.put(
        room['url'], {
            'title': 'thread1', 'body': 'thread1 description',
            'room': False, 'default_rights': None,
            'granted_rights': [], 'important': False, 'media': {}})
    assert response.status_code == 200
    thread1 = response.json()
    # make a second thread
    response = admin.put(
        room['url'], {
            'title': 'thread2', 'body': 'thread2 description',
            'room': False, 'default_rights': None,
            'granted_rights': [], 'important': False, 'media': {}})
    assert response.status_code == 200
    thread2 = response.json()
    # check not read is correct
    response = superuser.get(room_group['url'])
    assert response.status_code == 200
    data = response.json()
    assert data['rooms'][0]['not_read']['thread']['id'] == thread1['id']
    # delete first thread
    response = admin.delete(thread1['url'] + '?comment=bar')
    assert response.status_code == 200
    # check not read now
    response = superuser.get(room_group['url'])
    assert response.status_code == 200
    data = response.json()
    assert data['rooms'][0]['not_read']['thread']['id'] == thread2['id']
    # mark all as read
    response = superuser.post(room['url'] + 'read_mark/', {'comment_id': None})
    assert response.status_code == 200
    # check not read
    response = superuser.get(room_group['url'])
    assert response.status_code == 200
    data = response.json()
    assert data['rooms'][0]['not_read'] is None
    # restore thread
    response = superuser.put(thread1['url'] + 'restore/')
    assert response.status_code == 200
    # check not read is correct
    response = superuser.get(room_group['url'])
    assert response.status_code == 200
    data = response.json()
    assert data['rooms'][0]['not_read']['thread']['id'] == thread1['id']
