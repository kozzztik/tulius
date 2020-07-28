from tulius.forum.threads import models
from tulius.forum.rights import models as rights_models


def test_limited_read(room_group, thread, superuser, admin, user):
    # set no read to room
    response = superuser.put(
        room_group['url'] + 'granted_rights/', {
            'access_type': models.THREAD_ACCESS_TYPE_NO_READ
        }
    )
    assert response.status_code == 200
    # give rights to admin
    response = superuser.post(
        room_group['url'] + 'granted_rights/', {
            'user': {'id': admin.user.pk},
            'access_level': rights_models.THREAD_ACCESS_MODERATOR
        }
    )
    assert response.status_code == 200
    # set no read to thread
    response = admin.put(
        thread['url'] + 'granted_rights/', {
            'access_type': models.THREAD_ACCESS_TYPE_NO_READ
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
