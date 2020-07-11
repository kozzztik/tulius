import pytest


@pytest.mark.parametrize('value', [True, False])
def test_collapse_threads(room_group, user, client, value):
    # test anonymous user
    response = client.get('/api/forum/collapse/')
    assert response.status_code == 403
    # test normal user
    response = user.get('/api/forum/collapse/')
    assert response.status_code == 200
    # set collapse thread
    response = user.post(
        f'/api/forum/collapse/{room_group["id"]}', {'value': value})
    assert response.status_code == 200
    data = response.json()
    assert data == {'id': str(room_group['id']), 'value': value}
    # check it is returned
    response = user.get('/api/forum/collapse/')
    assert response.status_code == 200
    data = response.json()
    assert data[str(room_group['id'])] == value
    # set collapse thread False
    response = user.post(
        f'/api/forum/collapse/{room_group["id"]}', {'value': False})
    assert response.status_code == 200
    assert response.json() == {'id': str(room_group['id']), 'value': False}
    # check it is returned
    response = user.get('/api/forum/collapse/')
    assert response.status_code == 200
    data = response.json()
    assert not data[str(room_group['id'])]
