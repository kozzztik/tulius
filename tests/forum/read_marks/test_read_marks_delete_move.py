def test_readmark_delete_comment(room_group, superuser, admin, user):
    """
    superuser in this test is author, admin - user with readmark,
    user - without read mark, to cover all cases for counters state.
    """
    # create room
    response = superuser.put(
        room_group['url'], {
            'title': 'room', 'body': 'room description',
            'room': True, 'default_rights': None, 'granted_rights': []})
    assert response.status_code == 200
    room = response.json()
    # make a thread
    response = superuser.put(
        room['url'], {
            'title': 'thread', 'body': 'thread description',
            'room': False, 'default_rights': None,
            'granted_rights': [], 'important': False, 'media': {}})
    assert response.status_code == 200
    thread = response.json()
    # mark read by admin
    response = admin.post(
        thread['url'] + 'read_mark/',
        {'comment_id': thread['first_comment_id']})
    assert response.status_code == 200
    # add comment
    response = superuser.post(
        thread['url'] + 'comments_page/', {
            'reply_id': thread['first_comment_id'],
            'title': 'hello', 'body': 'world',
            'media': {},
        })
    assert response.status_code == 200
    data = response.json()
    comment = data['comments'][1]
    # check not read on room, direct read mark behavior initial state
    response = superuser.get(room['url'])
    assert response.status_code == 200
    data = response.json()
    assert data['threads'][0]['not_read'] is None
    # for admin
    response = admin.get(room['url'])
    assert response.status_code == 200
    data = response.json()
    assert data['threads'][0]['not_read']['id'] == comment['id']
    # for user
    response = user.get(room['url'])
    assert response.status_code == 200
    data = response.json()
    assert data['threads'][0]['not_read']['id'] == thread['first_comment_id']
    # check not read on index, read mark counters behavior initial state
    response = superuser.get('/api/forum/')
    assert response.status_code == 200
    rooms = {g['id']: g for g in response.json()['groups']}
    room_data = rooms[room_group['id']]
    assert room_data['not_read'] is None
    # for admin
    response = admin.get('/api/forum/')
    assert response.status_code == 200
    rooms = {g['id']: g for g in response.json()['groups']}
    room_data = rooms[room_group['id']]
    assert room_data['not_read']['id'] == comment['id']
    # for user
    response = user.get('/api/forum/')
    assert response.status_code == 200
    rooms = {g['id']: g for g in response.json()['groups']}
    room_data = rooms[room_group['id']]
    assert room_data['not_read']['id'] == thread['first_comment_id']
    # now delete last comment
    response = superuser.delete(comment['url'] + '?comment=foo')
    assert response.status_code == 200
    # check state on room
    response = superuser.get(room['url'])
    assert response.status_code == 200
    data = response.json()
    assert data['threads'][0]['not_read'] is None
    # for admin
    response = admin.get(room['url'])
    assert response.status_code == 200
    data = response.json()
    assert data['threads'][0]['not_read'] is None
    # for user
    response = user.get(room['url'])
    assert response.status_code == 200
    data = response.json()
    assert data['threads'][0]['not_read']['id'] == thread['first_comment_id']
    # check state for forum index
    response = superuser.get('/api/forum/')
    assert response.status_code == 200
    rooms = {g['id']: g for g in response.json()['groups']}
    room_data = rooms[room_group['id']]
    assert room_data['not_read'] is None
    # for admin
    response = admin.get('/api/forum/')
    assert response.status_code == 200
    rooms = {g['id']: g for g in response.json()['groups']}
    room_data = rooms[room_group['id']]
    assert room_data['not_read'] is None
    # for user
    response = user.get('/api/forum/')
    assert response.status_code == 200
    rooms = {g['id']: g for g in response.json()['groups']}
    room_data = rooms[room_group['id']]
    assert room_data['not_read']['id'] == thread['first_comment_id']


def test_readmark_delete_comment2(room_group, superuser, admin):
    """
    Create thread1, mark thread1 as read, add comment on thread1.
    create thread2. Check, delete comment. Thread 2 must became
    first not read for admin, thread 1 must be marked as read.
    """
    # create room
    response = superuser.put(
        room_group['url'], {
            'title': 'room', 'body': 'room description',
            'room': True, 'default_rights': None, 'granted_rights': []})
    assert response.status_code == 200
    room = response.json()
    # make a thread 1
    response = superuser.put(
        room['url'], {
            'title': 'thread1', 'body': 'thread1 description',
            'room': False, 'default_rights': None,
            'granted_rights': [], 'important': True, 'media': {}})
    assert response.status_code == 200
    thread1 = response.json()
    # mark read by admin
    response = admin.post(
        thread1['url'] + 'read_mark/',
        {'comment_id': thread1['first_comment_id']})
    assert response.status_code == 200
    # add comment
    response = superuser.post(
        thread1['url'] + 'comments_page/', {
            'reply_id': thread1['first_comment_id'],
            'title': 'hello', 'body': 'world',
            'media': {},
        })
    assert response.status_code == 200
    data = response.json()
    comment = data['comments'][1]
    # make a thread 2
    response = superuser.put(
        room['url'], {
            'title': 'thread2', 'body': 'thread1 description',
            'room': False, 'default_rights': None,
            'granted_rights': [], 'important': False, 'media': {}})
    assert response.status_code == 200
    thread2 = response.json()
    # check not read on room, direct read mark behavior initial state
    response = superuser.get(room['url'])
    assert response.status_code == 200
    data = response.json()
    assert data['threads'][0]['id'] == thread1['id']
    assert data['threads'][0]['not_read'] is None
    assert data['threads'][1]['not_read'] is None
    # for admin
    response = admin.get(room['url'])
    assert response.status_code == 200
    data = response.json()
    assert data['threads'][0]['id'] == thread1['id']
    assert data['threads'][0]['not_read']['id'] == comment['id']
    assert data['threads'][1]['not_read']['id'] == thread2['first_comment_id']
    # check not read on index, read mark counters behavior initial state
    response = superuser.get('/api/forum/')
    assert response.status_code == 200
    rooms = {g['id']: g for g in response.json()['groups']}
    room_data = rooms[room_group['id']]
    assert room_data['not_read'] is None
    # for admin
    response = admin.get('/api/forum/')
    assert response.status_code == 200
    rooms = {g['id']: g for g in response.json()['groups']}
    room_data = rooms[room_group['id']]
    assert room_data['not_read']['id'] == comment['id']
    # now delete last comment
    response = superuser.delete(comment['url'] + '?comment=foo')
    assert response.status_code == 200
    # check state on room
    response = superuser.get(room['url'])
    assert response.status_code == 200
    data = response.json()
    assert data['threads'][0]['id'] == thread1['id']
    assert data['threads'][0]['not_read'] is None
    assert data['threads'][1]['not_read'] is None
    # for admin
    response = admin.get(room['url'])
    assert response.status_code == 200
    data = response.json()
    assert data['threads'][0]['id'] == thread1['id']
    assert data['threads'][0]['not_read'] is None
    assert data['threads'][1]['not_read']['id'] == thread2['first_comment_id']
    # check state for forum index
    response = superuser.get('/api/forum/')
    assert response.status_code == 200
    rooms = {g['id']: g for g in response.json()['groups']}
    room_data = rooms[room_group['id']]
    assert room_data['not_read'] is None
    # for admin
    response = admin.get('/api/forum/')
    assert response.status_code == 200
    rooms = {g['id']: g for g in response.json()['groups']}
    room_data = rooms[room_group['id']]
    assert room_data['not_read']['id'] == thread2['first_comment_id']


def test_readmark_delete_thread(room_group, superuser, admin, user):
    """
    superuser in this test is author, admin - user with readmark,
    user - without read mark, to cover all cases for counters state.
    """
    # create room
    response = superuser.put(
        room_group['url'], {
            'title': 'room', 'body': 'room description',
            'room': True, 'default_rights': None, 'granted_rights': []})
    assert response.status_code == 200
    room = response.json()
    # make to threads
    response = superuser.put(
        room['url'], {
            'title': 'thread1', 'body': 'thread1 description',
            'room': False, 'default_rights': None,
            'granted_rights': [], 'important': True, 'media': {}})
    assert response.status_code == 200
    thread1 = response.json()
    response = superuser.put(
        room['url'], {
            'title': 'thread2', 'body': 'thread2 description',
            'room': False, 'default_rights': None,
            'granted_rights': [], 'important': False, 'media': {}})
    assert response.status_code == 200
    thread2 = response.json()
    # mark first thread as read
    response = admin.post(
        thread1['url'] + 'read_mark/',
        {'comment_id': thread1['first_comment_id']})
    assert response.status_code == 200
    # check not read on index, read mark counters behavior initial state
    response = superuser.get('/api/forum/')
    assert response.status_code == 200
    rooms = {g['id']: g for g in response.json()['groups']}
    room_data = rooms[room_group['id']]
    assert room_data['not_read'] is None
    # for admin
    response = admin.get('/api/forum/')
    assert response.status_code == 200
    rooms = {g['id']: g for g in response.json()['groups']}
    room_data = rooms[room_group['id']]
    assert room_data['not_read']['id'] == thread2['first_comment_id']
    # for user
    response = user.get('/api/forum/')
    assert response.status_code == 200
    rooms = {g['id']: g for g in response.json()['groups']}
    room_data = rooms[room_group['id']]
    assert room_data['not_read']['id'] == thread1['first_comment_id']
    # now delete first thread
    response = superuser.delete(thread1['url'] + '?comment=foo')
    assert response.status_code == 200
    # check state for forum index
    response = superuser.get('/api/forum/')
    assert response.status_code == 200
    rooms = {g['id']: g for g in response.json()['groups']}
    room_data = rooms[room_group['id']]
    assert room_data['not_read'] is None
    # for admin
    response = admin.get('/api/forum/')
    assert response.status_code == 200
    rooms = {g['id']: g for g in response.json()['groups']}
    room_data = rooms[room_group['id']]
    assert room_data['not_read']['id'] == thread2['first_comment_id']
    # for user
    response = user.get('/api/forum/')
    assert response.status_code == 200
    rooms = {g['id']: g for g in response.json()['groups']}
    room_data = rooms[room_group['id']]
    assert room_data['not_read']['id'] == thread2['first_comment_id']
    # delete second thread
    response = superuser.delete(thread2['url'] + '?comment=foo')
    assert response.status_code == 200
    # check state for forum index
    response = superuser.get('/api/forum/')
    assert response.status_code == 200
    rooms = {g['id']: g for g in response.json()['groups']}
    room_data = rooms[room_group['id']]
    assert room_data['not_read'] is None
    # for admin
    response = admin.get('/api/forum/')
    assert response.status_code == 200
    rooms = {g['id']: g for g in response.json()['groups']}
    room_data = rooms[room_group['id']]
    assert room_data['not_read'] is None
    # for user
    response = user.get('/api/forum/')
    assert response.status_code == 200
    rooms = {g['id']: g for g in response.json()['groups']}
    room_data = rooms[room_group['id']]
    assert room_data['not_read'] is None
