from tulius.forum import models


def test_read_marks(room_group, admin, user):
    # create a "real" room in group
    response = admin.put(
        room_group['url'], {
            'title': 'group1', 'body': 'group1 description',
            'room': True, 'access_type': 0, 'granted_rights': []})
    assert response.status_code == 200
    room = response.json()
    # make a thread for room
    response = admin.put(
        room['url'], {
            'title': 'thread', 'body': 'thread description',
            'room': False, 'access_type': 0, 'granted_rights': [],
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
    assert room_data['unreaded']['id'] == thread['first_comment_id']
    # check how it looks for admin
    response = admin.get('/api/forum/')
    assert response.status_code == 200
    data = response.json()
    rooms = {g['id']: g for g in data['groups']}
    room_data = rooms[room_group['id']]
    assert room_data['unreaded'] is None
    # mark first comment as read
    response = user.post(
        thread['url'] + 'read_mark/',
        {'comment_id': thread['first_comment_id']})
    assert response.status_code == 200
    data = response.json()
    assert data['last_read_id'] == thread['first_comment_id']
    assert data['not_read_comment']['id'] == comment['id']
    assert data['not_read_comment']['count'] == 1
    # check how it looks like on index
    response = user.get('/api/forum/')
    assert response.status_code == 200
    data = response.json()
    rooms = {g['id']: g for g in data['groups']}
    room_data = rooms[room_group['id']]
    assert room_data['unreaded']['id'] == comment['id']
    # check how it looks on room
    response = user.get(room['url'])
    assert response.status_code == 200
    data = response.json()
    assert data['threads'][0]['unreaded']['id'] == comment['id']
    # check how it looks on thread
    response = user.get(thread['url'])
    assert response.status_code == 200
    data = response.json()
    assert data['not_read_comment']['id'] == comment['id']
    assert data['not_read_comment']['count'] == 1
    # now mark all forum as read
    response = user.post('/api/forum/read_mark/', {'comment_id': None})
    assert response.status_code == 200
    data = response.json()
    assert data['last_read_id'] is None
    assert data['not_read_comment'] is None
    # check index
    response = user.get('/api/forum/')
    assert response.status_code == 200
    data = response.json()
    rooms = {g['id']: g for g in data['groups']}
    room_data = rooms[room_group['id']]
    assert room_data['unreaded'] is None
    # check room
    response = user.get(room['url'])
    assert response.status_code == 200
    data = response.json()
    assert data['threads'][0]['unreaded'] is None
    # check thread
    response = user.get(thread['url'])
    assert response.status_code == 200
    data = response.json()
    assert data['not_read_comment'] is None
    # Delete readmark
    response = user.delete(thread['url'] + 'read_mark/')
    assert response.status_code == 200
    data = response.json()
    assert data['last_read_id'] is None
    assert data['not_read_comment']['id'] == thread['first_comment_id']
    assert data['not_read_comment']['count'] == 2
    # check room
    response = user.get(room['url'])
    assert response.status_code == 200
    data = response.json()
    assert data['threads'][0]['unreaded']['id'] == thread['first_comment_id']


def test_readmark_rights(room_group, admin, user):
    # create a "real" room in group
    response = admin.put(
        room_group['url'], {
            'title': 'group1', 'body': 'group1 description',
            'room': True, 'access_type': 0, 'granted_rights': []})
    assert response.status_code == 200
    room = response.json()
    # make a thread for room
    response = admin.put(
        room['url'], {
            'title': 'thread', 'body': 'thread description',
            'room': False, 'access_type': models.THREAD_ACCESS_TYPE_NO_READ,
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
    assert data['not_read_comment'] is None
    # open thread
    response = admin.put(
        thread['url'] + 'granted_rights/', {
            'access_type': models.THREAD_ACCESS_TYPE_NOT_SET
        }
    )
    assert response.status_code == 200
    # check how it looks now on index
    response = user.get('/api/forum/')
    assert response.status_code == 200
    data = response.json()
    rooms = {g['id']: g for g in data['groups']}
    room_data = rooms[room_group['id']]
    assert room_data['unreaded']['id'] == thread['first_comment_id']

