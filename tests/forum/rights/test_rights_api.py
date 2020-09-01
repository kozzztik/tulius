from tulius.forum.threads import models


def test_update_and_moderate(client, superuser, admin, user):
    # create root room
    response = superuser.put(
        '/api/forum/', {
            'title': 'group', 'body': 'group description',
            'room': True, 'default_rights': None, 'granted_rights': []})
    assert response.status_code == 200
    group = response.json()
    # create target room
    response = admin.put(
        group['url'], {
            'title': 'room', 'body': 'room description',
            'room': True, 'default_rights': None, 'granted_rights': []})
    assert response.status_code == 200
    room = response.json()
    # check empty rights
    response = admin.get(room['url'] + 'granted_rights/')
    assert response.status_code == 200
    data = response.json()
    assert data['granted_rights'] == []
    # check options
    response = admin.options(
        room['url'] + 'granted_rights/?query=' + user.user.username)
    assert response.status_code == 200
    data = response.json()
    assert len(data['users']) == 1
    assert data['users'][0]['id'] == user.user.pk
    # check rights for not privileged users not works
    response = user.get(room['url'] + 'granted_rights/')
    assert response.status_code == 403
    # check thread readable by user
    response = user.get(room['url'])
    assert response.status_code == 200
    # check user can't change thread access type
    response = user.put(
        room['url'] + 'granted_rights/',
        {'default_rights': models.NO_ACCESS})
    assert response.status_code == 403
    # check user can't give privileges
    response = user.post(
        room['url'] + 'granted_rights/',
        {
            'user': {'id': user.user.pk},
            'access_level': models.ACCESS_READ
        })
    assert response.status_code == 403
    # set it "no read"
    response = admin.put(
        room['url'] + 'granted_rights/',
        {'default_rights': models.NO_ACCESS})
    assert response.status_code == 200
    # check user now can't access room
    response = user.get(room['url'])
    assert response.status_code == 403
    # give user access
    response = admin.post(
        room['url'] + 'granted_rights/',
        {
            'user': {'id': user.user.pk},
            'access_level': models.ACCESS_READ
        })
    assert response.status_code == 200
    # check now room is visible
    response = user.get(room['url'])
    assert response.status_code == 200
    # load rights
    response = admin.get(room['url'] + 'granted_rights/')
    assert response.status_code == 200
    data = response.json()
    assert len(data['granted_rights']) == 1
    assert data['granted_rights'][0]['user']['id'] == user.user.pk
    right = data['granted_rights'][0]
    # check user still can't read rights
    response = user.get(room['url'] + 'granted_rights/')
    assert response.status_code == 403
    # check user can't promote himself
    response = user.get(room['url'] + f'granted_rights/{right["id"]}/')
    assert response.status_code == 403
    right['access_level'] = models.ACCESS_MODERATOR
    response = user.post(room['url'] + f'granted_rights/{right["id"]}/', right)
    assert response.status_code == 403
    # promote user
    response = admin.post(
        room['url'] + f'granted_rights/{right["id"]}/', right)
    assert response.status_code == 200
    response = user.get(room['url'] + f'granted_rights/{right["id"]}/')
    assert response.status_code == 200
    data = response.json()
    assert data['access_level'] == models.ACCESS_MODERATOR
    # check now rights
    response = user.get(room['url'] + 'granted_rights/')
    assert response.status_code == 200
    # delete right
    response = admin.delete(room['url'] + f'granted_rights/{right["id"]}/')
    assert response.status_code == 200
    # now can't read room again
    response = user.get(room['url'])
    assert response.status_code == 403
    # create rights for user to read and check he can't delete it
    response = admin.post(
        room['url'] + 'granted_rights/',
        {
            'user': {'id': user.user.pk},
            'access_level': models.ACCESS_READ
        })
    assert response.status_code == 200
    right = response.json()
    response = user.delete(room['url'] + f'granted_rights/{right["id"]}/')
    assert response.status_code == 403
