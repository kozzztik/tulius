from tulius.forum.threads import models


def test_no_inherit_at_root(superuser, admin):
    # create root room
    response = superuser.put(
        '/api/forum/', {
            'title': 'group', 'body': 'group description',
            'room': True,
            'default_rights': models.ACCESS_READ + models.ACCESS_NO_INHERIT,
            'granted_rights': []})
    assert response.status_code == 200
    group = response.json()
    # create target room
    response = superuser.put(
        group['url'], {
            'title': 'room', 'body': 'room description',
            'room': True, 'default_rights': None, 'granted_rights': []})
    assert response.status_code == 200
    room = response.json()
    # check user can read root room and can't write there
    response = admin.get(group['url'])
    assert response.status_code == 200
    response = admin.put(
        group['url'], {
            'title': 'room', 'body': 'room description',
            'room': True, 'default_rights': None, 'granted_rights': []})
    assert response.status_code == 403
    # check we can read and write to subroom
    response = admin.get(room['url'])
    assert response.status_code == 200
    response = admin.put(
        room['url'], {
            'title': 'room', 'body': 'room description',
            'room': True, 'default_rights': None, 'granted_rights': []})
    assert response.status_code == 200


def test_no_inherit_in_room(superuser, admin, room_group):
    # create root room
    response = superuser.put(
        room_group['url'], {
            'title': 'group', 'body': 'group description',
            'room': True,
            'default_rights': models.ACCESS_READ + models.ACCESS_NO_INHERIT,
            'granted_rights': []})
    assert response.status_code == 200
    room1 = response.json()
    # create target room
    response = superuser.put(
        room1['url'], {
            'title': 'room', 'body': 'room description',
            'room': True, 'default_rights': None, 'granted_rights': []})
    assert response.status_code == 200
    room2 = response.json()
    # check user can read root room and can't write there
    response = admin.get(room1['url'])
    assert response.status_code == 200
    response = admin.put(
        room1['url'], {
            'title': 'room', 'body': 'room description',
            'room': True, 'default_rights': None, 'granted_rights': []})
    assert response.status_code == 403
    # check we can read and write to subroom
    response = admin.get(room2['url'])
    assert response.status_code == 200
    response = admin.put(
        room2['url'], {
            'title': 'room', 'body': 'room description',
            'room': True, 'default_rights': None, 'granted_rights': []})
    assert response.status_code == 200
