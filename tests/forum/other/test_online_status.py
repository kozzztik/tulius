def test_online_status(thread, admin, user):
    # check online on thread
    response = admin.get(f'/api/forum/online_status/{thread["id"]}/')
    assert response.status_code == 200
    data = response.json()
    assert len(data['users']) == 1
    assert data['users'][0]['id'] == admin.user.pk
    # check online by other user
    response = user.get(f'/api/forum/online_status/{thread["id"]}/')
    assert response.status_code == 200
    data = response.json()
    assert len(data['users']) == 2
    assert data['users'][0]['id'] == admin.user.pk
    assert data['users'][1]['id'] == user.user.pk
    # check online on root
    response = admin.get(f'/api/forum/online_status/')
    assert response.status_code == 200
    data = response.json()
    assert len(data['users']) >= 2
    ids = [u['id'] for u in data['users']]
    assert admin.user.pk in ids
    assert user.user.pk in ids

