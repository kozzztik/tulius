from tulius.forum import models
from tulius.forum.rights import default


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
            'access_level': models.THREAD_ACCESS_MODERATOR
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


def test_rights_for_deleted_thread(thread, superuser, admin, user):
    # delete thread
    response = admin.delete(thread['url'] + '?comment=wow')
    assert response.status_code == 200
    obj = models.Thread.objects.get(pk=thread['id'])
    # check rights for superuser
    rights = default.DefaultRightsChecker(obj, superuser.user).get_rights()
    assert rights.read
    assert not rights.write
    assert rights.moderate
    # check rights for owner
    rights = default.DefaultRightsChecker(obj, admin.user).get_rights()
    assert rights.read
    assert not rights.write
    assert not rights.moderate
    # check rights for simple user
    rights = default.DefaultRightsChecker(obj, user.user).get_rights()
    assert not rights.read
    assert not rights.write
    assert not rights.moderate
