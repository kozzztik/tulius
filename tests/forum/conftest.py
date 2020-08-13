import pytest


@pytest.fixture(name='room_group')
def room_group_fixture(superuser):
    response = superuser.put(
        '/api/forum/', {
            'title': 'group1', 'body': 'group1 description',
            'room': True, 'default_rights': None, 'granted_rights': []})
    assert response.status_code == 200
    return response.json()


@pytest.fixture(name='thread')
def thread_fixture(room_group, admin):
    response = admin.put(
        room_group['url'], {
            'title': 'thread', 'body': 'thread description',
            'room': False, 'default_rights': None, 'granted_rights': [],
            'important': False, 'media': {}})
    assert response.status_code == 200
    return response.json()
