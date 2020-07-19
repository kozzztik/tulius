import pytest

from tulius.forum import models
from tulius.forum.threads import signals


@pytest.mark.parametrize('on_room', [False, True])
def test_fix_counters_api(room_group, thread, superuser, admin, on_room):
    # check api works only for superuser
    response = admin.post('/api/forum/fix/')
    assert response.status_code == 403
    # break thread tree_id
    obj = models.Thread.objects.get(pk=thread['id'])
    orig_tree_id = obj.tree_id
    obj.tree_id += 1
    obj.save()
    # check it works for root
    if on_room:
        response = superuser.post(room_group["url"] + 'fix/')
    else:
        response = superuser.post('/api/forum/fix/')
    assert response.status_code == 200
    data = response.json()
    assert data['result']['threads'] > 0
    # check tree_id is fixed
    obj = models.Thread.objects.get(pk=thread['id'])
    assert obj.tree_id == orig_tree_id


def _my_receiver_action(thread):
    thread.media['foo'] = 'bar'
    return _my_receiver_action


def _my_receiver(sender, thread, **kwargs):
    thread.media['bar'] = 'foo'
    return _my_receiver_action


def test_fix_parent_call(room_group, superuser):
    # create room in group
    response = superuser.put(
        room_group['url'], {
            'title': 'group', 'body': 'group description',
            'room': True, 'access_type': 0, 'granted_rights': []})
    assert response.status_code == 200
    room = response.json()
    # create thread
    response = superuser.put(
        room['url'], {
            'title': 'thread', 'body': 'thread description',
            'room': False,
            'access_type': models.THREAD_ACCESS_TYPE_NOT_SET,
            'granted_rights': [], 'important': False, 'media': {}})
    assert response.status_code == 200
    thread = response.json()
    # do "fix"
    signals.on_fix_counters.connect(_my_receiver)
    try:
        response = superuser.post(room_group["url"] + 'fix/')
    finally:
        assert signals.on_fix_counters.disconnect(_my_receiver)
    assert response.status_code == 200
    data = response.json()
    assert data['result']['threads'] == 3
    # check thread
    response = superuser.get(thread['url'])
    assert response.status_code == 200
    thread = response.json()
    assert thread['media']['bar'] == 'foo'
    # check room
    obj = models.Thread.objects.get(pk=room['id'])
    assert obj.media['foo'] == 'bar'
    # check room group
    obj = models.Thread.objects.get(pk=room_group['id'])
    assert obj.media['foo'] == 'bar'
