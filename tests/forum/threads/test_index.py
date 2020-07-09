from tulius.forum import models


def test_index(client, superuser, admin, user):
    response = client.get('/api/forum/')
    assert response.status_code == 200
    # simple user can't create rooms at root
    response = user.put(
        '/api/forum/', {
            'title': 'group1', 'body': 'group1 description',
            'room': True, 'access_type': 0, 'granted_rights': []})
    assert response.status_code == 403
    #
    #   superuser actions
    #
    response = superuser.put(
        '/api/forum/', {
            'title': 'group1', 'body': 'group1 description',
            'room': False, 'access_type': 0, 'granted_rights': []})
    assert response.status_code == 403
    response = superuser.put(
        '/api/forum/', {
            'title': 'group1', 'body': 'group1 description',
            'room': True, 'access_type': 0, 'granted_rights': []})
    assert response.status_code == 200
    group1 = response.json()
    response = superuser.put(
        '/api/forum/', {
            'title': 'group2', 'body': 'group2 description',
            'room': True, 'access_type': models.THREAD_ACCESS_TYPE_NO_WRITE,
            'granted_rights': [{
                'user': {'id': admin.user.pk},
                'access_level': models.THREAD_ACCESS_WRITE}]})
    assert response.status_code == 200
    group2 = response.json()
    response = superuser.put(
        '/api/forum/', {
            'title': 'group3', 'body': 'group3 description',
            'room': True, 'access_type': models.THREAD_ACCESS_TYPE_NO_READ,
            'granted_rights': [{
                'user': {'id': admin.user.pk},
                'access_level': models.THREAD_ACCESS_READ}]})
    assert response.status_code == 200
    group3 = response.json()
    #
    #  admin user actions
    #
    response = admin.get('/api/forum/')
    assert response.status_code == 200
    groups = {g['id']: g for g in response.json()['groups']}
    assert group1['id'] in groups
    assert group2['id'] in groups
    assert group3['id'] in groups
    response = admin.put(
        f"/api/forum/thread/{group1['id']}/", {
            'title': 'room1', 'body': 'room1 description',
            'room': True, 'access_type': models.THREAD_ACCESS_TYPE_OPEN,
            'granted_rights': [{
                'user': {'id': admin.user.pk},
                'access_level': models.THREAD_ACCESS_READ}]})
    assert response.status_code == 200
    room1 = response.json()
    response = admin.put(
        f"/api/forum/thread/{group2['id']}/", {
            'title': 'room2', 'body': 'room2 description',
            'room': True, 'access_type': 0,
            'granted_rights': []})
    assert response.status_code == 200
    room2 = response.json()
    response = admin.put(
        f"/api/forum/thread/{group3['id']}/", {
            'title': 'room3', 'body': 'room3 description',
            'room': True, 'access_type': 0,
            'granted_rights': []})
    assert response.status_code == 403
    #
    # simple user actions
    #
    response = user.get('/api/forum/')
    assert response.status_code == 200
    groups = {g['id']: g for g in response.json()['groups']}
    assert group1['id'] in groups
    assert group2['id'] in groups
    assert group3['id'] not in groups
    rooms = {r['id']: r for r in groups[group1['id']]['rooms']}
    assert room1['id'] in rooms
    rooms = {r['id']: r for r in groups[group2['id']]['rooms']}
    assert room2['id'] in rooms
    response = user.put(
        f"/api/forum/thread/{group2['id']}/", {
            'title': 'thread1', 'body': 'thread1 description',
            'room': False, 'access_type': 0,
            'granted_rights': []})
    assert response.status_code == 403
    response = user.put(
        f"/api/forum/thread/{group1['id']}/", {
            'title': 'thread1', 'body': 'thread1 description',
            'room': False, 'access_type': 0, 'media': {},
            'granted_rights': []})
    assert response.status_code == 200
    thread1 = response.json()
    #
    # again superuser
    #
    response = superuser.get('/api/forum/')
    assert response.status_code == 200
    groups = {g['id']: g for g in response.json()['groups']}
    group1 = groups[group1['id']]
    assert group1['rooms'][0]['id'] == room1['id']
    assert 'threads' not in group1
