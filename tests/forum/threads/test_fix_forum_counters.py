import pytest

from tulius.forum.threads import models


@pytest.mark.parametrize('on_room', [False, True])
def test_fix_counters_api(room_group, thread, superuser, admin, on_room):
    # check api works only for superuser
    response = admin.post('/api/forum/fix/')
    assert response.status_code == 403
    # break thread tree_id
    obj = models.Thread.objects.get(pk=thread['id'])
    orig_parents = obj.parents_ids
    obj.parents_ids = None
    obj.save()
    # check it works for root
    if on_room:
        response = superuser.post(room_group["url"] + 'fix/')
    else:
        response = superuser.post('/api/forum/fix/')
    assert response.status_code == 200
    data = response.json()
    assert data['result']['threads'] > 0
    # check parents is fixed
    obj = models.Thread.objects.get(pk=thread['id'])
    assert obj.parents_ids == orig_parents
