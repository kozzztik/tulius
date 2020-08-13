from tulius.forum.threads import models


def test_limited_read(room_group, thread, superuser, admin, user):
    # set no read to room
    response = superuser.put(
        room_group['url'] + 'granted_rights/', {
            'default_rights': models.NO_ACCESS
        }
    )
    assert response.status_code == 200
    # give rights to admin
    response = superuser.post(
        room_group['url'] + 'granted_rights/', {
            'user': {'id': admin.user.pk},
            'access_level': models.ACCESS_MODERATOR
        }
    )
    assert response.status_code == 200
    # set no read to thread
    response = admin.put(
        thread['url'] + 'granted_rights/', {
            'default_rights': models.NO_ACCESS
        }
    )
    assert response.status_code == 200
    # check how it looks on room
    response = admin.get(room_group['url'])
    assert response.status_code == 200
    data = response.json()
    limited_read = data['threads'][0]['accessed_users']
    assert len(limited_read) == 1
    assert limited_read[0]['id'] == admin.user.pk
