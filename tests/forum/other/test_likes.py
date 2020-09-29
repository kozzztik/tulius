from tulius.forum.threads import models


def test_setting_likes(thread, user, superuser):
    # load like mark
    comment_id = thread['first_comment_id']
    response = user.get(f'/api/forum/likes/?ids={comment_id}')
    assert response.status_code == 200
    data = response.json()
    assert str(comment_id) in data
    assert not data[str(comment_id)]
    # check that favorites is empty
    response = user.get('/api/forum/favorites/')
    assert response.status_code == 200
    data = response.json()
    assert data['groups'][0]['items'] == []
    # set like mark
    response = user.post(
        '/api/forum/likes/', {'id': comment_id, 'value': True})
    assert response.status_code == 200
    data = response.json()
    assert data == {'value': True}
    # check it is returned through API
    response = user.get(f'/api/forum/likes/?ids={comment_id}')
    assert response.status_code == 200
    data = response.json()
    assert str(comment_id) in data
    assert data[str(comment_id)]
    # check favorites
    response = user.get('/api/forum/favorites/')
    assert response.status_code == 200
    data = response.json()
    assert len(data['groups'][0]['items']) == 1
    assert data['groups'][0]['items'][0]['comment']['id'] == comment_id
    assert data['groups'][0]['items'][0]['thread']['id'] == thread['id']
    # remove like mark
    response = user.post(
        '/api/forum/likes/', {'id': comment_id, 'value': False})
    assert response.status_code == 200
    data = response.json()
    assert data == {'value': False}
    # check that favorites is empty
    response = user.get('/api/forum/favorites/')
    assert response.status_code == 200
    data = response.json()
    assert data['groups'][0]['items'] == []
    # check API
    response = user.get(f'/api/forum/likes/?ids={comment_id}')
    assert response.status_code == 200
    data = response.json()
    assert str(comment_id) in data
    assert not data[str(comment_id)]


def test_rights_check_in_favorites(thread, user, superuser):
    comment_id = thread['first_comment_id']
    # set like mark
    response = user.post(
        '/api/forum/likes/', {'id': comment_id, 'value': True})
    assert response.status_code == 200
    data = response.json()
    assert data == {'value': True}
    # check it is returned through API
    response = user.get(f'/api/forum/likes/?ids={comment_id}')
    assert response.status_code == 200
    data = response.json()
    assert str(comment_id) in data
    assert data[str(comment_id)]
    # check favorites
    response = user.get('/api/forum/favorites/')
    assert response.status_code == 200
    data = response.json()
    assert len(data['groups'][0]['items']) == 1
    assert data['groups'][0]['items'][0]['comment']['id'] == comment_id
    assert data['groups'][0]['items'][0]['thread']['id'] == thread['id']
    # remove read rights
    response = superuser.put(
        thread['url'] + 'granted_rights/', {'default_rights': models.NO_ACCESS}
    )
    assert response.status_code == 200
    # check we can double like
    response = user.post(
        '/api/forum/likes/', {'id': comment_id, 'value': True})
    assert response.status_code == 200
    # check we still can remove like
    response = user.post(
        '/api/forum/likes/', {'id': comment_id, 'value': False})
    assert response.status_code == 200
    # but not set it back
    response = user.post(
        '/api/forum/likes/', {'id': comment_id, 'value': True})
    assert response.status_code == 403
    # check favorites
    response = user.get('/api/forum/favorites/')
    assert response.status_code == 200
    data = response.json()
    assert data['groups'][0]['items'] == []


def test_liking_not_existing_comment(thread, user):
    comment_id = thread['first_comment_id']
    # set like mark for not created comment
    response = user.post(
        '/api/forum/likes/', {'id': comment_id + 1, 'value': True})
    assert response.status_code == 404


def test_double_liking(thread, user):
    comment_id = thread['first_comment_id']
    # set like mark
    response = user.post(
        '/api/forum/likes/', {'id': comment_id, 'value': True})
    assert response.status_code == 200
    data = response.json()
    assert data == {'value': True}
    # set like mark again
    response = user.post(
        '/api/forum/likes/', {'id': comment_id, 'value': True})
    assert response.status_code == 200
    data = response.json()
    assert data == {'value': True}
    # check it is returned through API
    response = user.get(f'/api/forum/likes/?ids={comment_id}')
    assert response.status_code == 200
    data = response.json()
    assert str(comment_id) in data
    assert data[str(comment_id)]
    # Remove
    response = user.post(
        '/api/forum/likes/', {'id': comment_id, 'value': False})
    assert response.status_code == 200
    data = response.json()
    assert data == {'value': False}
    # check it is returned through API
    response = user.get(f'/api/forum/likes/?ids={comment_id}')
    assert response.status_code == 200
    data = response.json()
    assert str(comment_id) in data
    assert not data[str(comment_id)]
    # remove again
    response = user.post(
        '/api/forum/likes/', {'id': comment_id, 'value': False})
    assert response.status_code == 200
    data = response.json()
    assert data == {'value': False}
    # check it is returned through API
    response = user.get(f'/api/forum/likes/?ids={comment_id}')
    assert response.status_code == 200
    data = response.json()
    assert str(comment_id) in data
    assert not data[str(comment_id)]
