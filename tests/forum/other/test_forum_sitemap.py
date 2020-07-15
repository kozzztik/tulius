from xml.etree import ElementTree

import pytest

from tulius.forum import models


@pytest.mark.parametrize('path', ['/sitemap-forum.xml', '/forums/sitemap.xml'])
def test_sitemap(room_group, thread, client, path, superuser):
    # create thread with no read access
    response = superuser.put(
        room_group['url'], {
            'title': 'thread', 'body': 'thread description',
            'room': False, 'access_type': models.THREAD_ACCESS_TYPE_NO_READ,
            'granted_rights': [], 'important': True, 'media': {}})
    assert response.status_code == 200
    thread2 = response.json()
    # retrieve sitemap
    response = client.get(path)
    assert response.status_code == 200
    data = ElementTree.fromstring(response.content)
    # check contents
    found = False
    for thread_data in data:
        loc = thread_data[0].text
        # check that rooms and "no read" threads are not in sitemap
        assert loc != f'http://example.com/forums/thread/{room_group["id"]}/'
        assert loc != f'http://example.com/forums/thread/{thread2["id"]}/'
        if loc == f'http://example.com/forums/thread/{thread["id"]}/':
            found = True
    assert found
