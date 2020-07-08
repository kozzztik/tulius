from tulius.forum import models


def test_update_and_moderate(client, superuser, admin, user):
    # create root room
    response = superuser.put(
        '/api/forum/', {
            'title': 'group', 'body': 'group description',
            'room': True, 'access_type': 0, 'granted_rights': []},
        content_type='application/json')
    assert response.status_code == 200
    group = response.json()
    # check that for privileged user important works, but not closed
    response = superuser.put(
        group['url'], {
            'title': 'thread', 'body': 'thread description',
            'room': False, 'access_type': 0, 'granted_rights': [],
            'important': True, 'closed': True, 'media': {}},
        content_type='application/json')
    assert response.status_code == 200
    su_thread = response.json()
    assert su_thread['important']
    assert not su_thread['closed']
    # create thread by admin without moderate. Check that "important" and
    # closed doesn't works.
    response = admin.put(
        group['url'], {
            'title': 'thread', 'body': 'thread description',
            'room': False, 'access_type': 0, 'granted_rights': [],
            'important': True, 'closed': True, 'media': {}},
        content_type='application/json')
    assert response.status_code == 200
    thread = response.json()
    assert not thread['important']
    assert not thread['closed']
    # check that update not works too
    response = admin.post(
        thread['url'], {
            'title': 'thread(updated)', 'body': 'thread description2',
            'access_type': models.THREAD_ACCESS_TYPE_NO_READ,
            'granted_rights': [],
            'important': True, 'closed': True, 'media': {}},
        content_type='application/json')
    assert response.status_code == 200
    updated = response.json()
    assert not updated['important']
    assert not updated['closed']
    assert updated['title'] == 'thread(updated)'
    assert updated['body'] == 'thread description2'
    assert updated['access_type'] == 0
    # check that not privileged user can't edit thread
    response = user.post(
        thread['url'], {
            'title': 'thread(updated)', 'body': 'thread description3',
            'access_type': 0, 'granted_rights': [],
            'important': True, 'closed': True, 'media': {}},
        content_type='application/json')
    assert response.status_code == 403
    # add privileges
    response = superuser.post(
        thread['url'] + 'granted_rights/', {
            'user': {'id': admin.user.pk},
            'access_level': models.THREAD_ACCESS_MODERATE
        }, content_type='application/json'
    )
    assert response.status_code == 200
    response = superuser.put(
        thread['url'] + 'granted_rights/', {
            'access_type': models.THREAD_ACCESS_TYPE_NO_READ
        }, content_type='application/json'
    )
    assert response.status_code == 200
    # check how it looks like on room page for anonymous user
    response = client.get(group['url'])
    assert response.status_code == 200
    room = response.json()
    assert len(room['threads']) == 1
    assert room['threads'][0]['id'] == su_thread['id']
    response = client.get(thread['url'])
    assert response.status_code == 403
    # check how it looks like on room page for privileged user
    response = admin.get(group['url'])
    assert response.status_code == 200
    room = response.json()
    assert len(room['threads']) == 2
    assert room['threads'][0]['id'] == su_thread['id']
    assert len(room['threads'][0]['moderators']) == 0
    assert room['threads'][0]['accessed_users'] is None
    assert room['threads'][1]['id'] == thread['id']
    assert len(room['threads'][1]['accessed_users']) == 1
    assert room['threads'][1]['accessed_users'][0]['id'] == admin.user.pk
    assert len(room['threads'][1]['moderators']) == 1
    assert room['threads'][1]['moderators'][0]['id'] == admin.user.pk
    # check new permissions
    response = admin.post(
        thread['url'], {
            'title': 'thread(updated3)', 'body': 'thread description3',
            'granted_rights': [],
            'important': True, 'closed': True, 'media': {}},
        content_type='application/json')
    assert response.status_code == 200
    updated = response.json()
    assert updated['important']
    assert updated['closed']
    assert updated['title'] == 'thread(updated3)'
    assert updated['body'] == 'thread description3'
    # check room update works too, and 'room' is ignored
    response = superuser.post(
        group['url'], {
            'title': 'group(updated)', 'body': 'group description(updated)',
            'room': False, 'access_type': models.THREAD_ACCESS_TYPE_NO_READ},
        content_type='application/json')
    assert response.status_code == 200
    data = response.json()
    assert data['title'] == 'group(updated)'
    assert data['body'] == 'group description(updated)'
    assert data['room']
    assert data['access_type'] == 0
