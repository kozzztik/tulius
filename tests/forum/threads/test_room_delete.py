from tulius.forum import models


def test_room_delete(client, superuser, admin, user):
    # create root room
    response = superuser.put(
        '/api/forum/', {
            'title': 'group', 'body': 'group description',
            'room': True, 'access_type': 0, 'granted_rights': []},
        content_type='application/json')
    assert response.status_code == 200
    # Create rooms in root room
    group = response.json()
    response = admin.put(
        group['url'], {
            'title': 'room1', 'body': 'room1 description',
            'room': True, 'access_type': models.THREAD_ACCESS_TYPE_OPEN,
            'granted_rights': []},
        content_type='application/json')
    assert response.status_code == 200
    room1 = response.json()
    response = admin.put(
        group['url'], {
            'title': 'room2', 'body': 'room2 description',
            'room': True, 'access_type': models.THREAD_ACCESS_TYPE_OPEN,
            'granted_rights': []},
        content_type='application/json')
    assert response.status_code == 200
    room2 = response.json()
    # Create branch of rooms in room1 to test delete in middle of branch
    response = admin.put(
        room1['url'], {
            'title': 'room3', 'body': 'room3 description',
            'room': True, 'access_type': models.THREAD_ACCESS_TYPE_OPEN,
            'granted_rights': []},
        content_type='application/json')
    assert response.status_code == 200
    room3 = response.json()
    response = admin.put(
        room3['url'], {
            'title': 'room4', 'body': 'room4 description',
            'room': True, 'access_type': models.THREAD_ACCESS_TYPE_OPEN,
            'granted_rights': []},
        content_type='application/json')
    assert response.status_code == 200
    room4 = response.json()
    # Create threads to check how they will be filtered by room delete
    for room in [room1, room2, room4]:
        response = admin.put(
            room['url'], {
                'title': 'thread1', 'body': 'thread1 description',
                'room': False, 'access_type': models.THREAD_ACCESS_TYPE_OPEN,
                'granted_rights': [], 'media': {}},
            content_type='application/json')
        assert response.status_code == 200
    # Check initial state, that before delete it looks like expected
    response = admin.get(group['url'])
    assert response.status_code == 200
    data = response.json()
    assert len(data['rooms']) == 2
    assert data['rooms'][0]['id'] == room1['id']
    assert data['rooms'][0]['threads_count'] == 2
    assert data['rooms'][1]['id'] == room2['id']
    assert data['rooms'][1]['threads_count'] == 1
    # Try delete by not expected user
    response = user.delete(room3['url'] + '?comment=oow')
    assert response.status_code == 403
    # Do actual delete inside of branch
    response = admin.delete(room3['url'] + '?comment=oow')
    assert response.status_code == 200
    # Check how it looks like by anonymous user
    response = client.get(group['url'])
    assert response.status_code == 200
    data = response.json()
    assert len(data['rooms']) == 2
    assert data['rooms'][0]['id'] == room1['id']
    assert data['rooms'][0]['threads_count'] == 1
    assert data['rooms'][1]['id'] == room2['id']
    assert data['rooms'][1]['threads_count'] == 1
    # Do delete of child, not inside of branch
    response = admin.delete(room2['url'] + '?comment=oow')
    assert response.status_code == 200
    # Check again how it looks like now
    response = admin.get(group['url'])
    assert response.status_code == 200
    data = response.json()
    assert len(data['rooms']) == 1
    assert data['rooms'][0]['id'] == room1['id']
    assert data['rooms'][0]['threads_count'] == 1
