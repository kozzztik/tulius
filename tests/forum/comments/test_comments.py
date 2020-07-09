from tulius.forum import models


def test_comments_api(client, superuser, admin, user):
    # create root room and thread in it
    response = superuser.put(
        '/api/forum/', {
            'title': 'group', 'body': 'group description',
            'room': True, 'access_type': 0, 'granted_rights': []})
    assert response.status_code == 200
    group = response.json()
    response = admin.put(
        group['url'], {
            'title': 'thread', 'body': 'thread description',
            'room': False, 'access_type': models.THREAD_ACCESS_TYPE_NO_READ,
            'granted_rights': [], 'media': {}})
    assert response.status_code == 200
    thread = response.json()
    # check comments not readable for other users
    response = user.get(thread['url'] + 'comments_page/')
    assert response.status_code == 403
    # make thread readable
    response = admin.put(
        thread['url'] + 'granted_rights/', {
            'access_type': models.THREAD_ACCESS_TYPE_NO_WRITE
        })
    assert response.status_code == 200
    # check user now can read comments
    response = user.get(thread['url'] + 'comments_page/')
    assert response.status_code == 200
    data = response.json()
    assert len(data['comments']) == 1
    first_comment = data['comments'][0]
    assert first_comment['title'] == 'thread'
    assert first_comment['body'] == 'thread description'
    assert first_comment['is_thread']
    assert not first_comment['edit_right']

    # check that user can't post comments
    response = user.post(
        thread['url'] + 'comments_page/', {
            'reply_id': first_comment['id'],
            'title': 'hello', 'body': 'world',
            'media': {},
        })
    assert response.status_code == 403

    # make thread opened
    response = admin.put(
        thread['url'] + 'granted_rights/', {
            'access_type': models.THREAD_ACCESS_TYPE_NOT_SET
        }
    )
    assert response.status_code == 200
    # check comment preview works
    response = user.post(
        thread['url'] + 'comments_page/', {
            'reply_id': first_comment['id'],
            'title': 'hello', 'body': 'world',
            'media': {}, 'preview': True,
        })
    assert response.status_code == 200
    data = response.json()
    assert data['id'] is None
    assert data['user']['id'] == user.user.pk
    assert data['title'] == 'hello'
    assert data['body'] == 'world'
    # check that comment really not created
    response = user.get(thread['url'] + 'comments_page/')
    assert response.status_code == 200
    data = response.json()
    assert len(data['comments']) == 1

    # now really post comment
    response = user.post(
        thread['url'] + 'comments_page/', {
            'reply_id': first_comment['id'],
            'title': 'hello', 'body': 'world',
            'media': {},
        })
    assert response.status_code == 200
    data = response.json()
    assert len(data['comments']) == 2
    comment = data['comments'][1]
    assert comment['id']
    assert comment['user']['id'] == user.user.pk
    assert comment['title'] == 'hello'
    assert comment['body'] == 'world'
    # check user can update his comment
    response = user.post(
        comment['url'], {
            'reply_id': first_comment['id'],
            'title': 'hello world', 'body': 'world is great',
            'media': {},
        })
    assert response.status_code == 200
    data = response.json()
    assert data['id'] == comment['id']
    assert data['title'] == 'hello world'
    assert data['body'] == 'world is great'
    # check it is really updated
    response = user.get(comment['url'])
    assert response.status_code == 200
    data = response.json()
    assert data['id'] == comment['id']
    assert data['title'] == 'hello world'
    assert data['body'] == 'world is great'
    # delete comment
    response = user.delete(comment['url'] + '?comment=wow')
    assert response.status_code == 200
    # check it is deleted
    response = user.get(thread['url'] + 'comments_page/')
    assert response.status_code == 200
    data = response.json()
    assert len(data['comments']) == 1
    assert data['comments'][0]['id'] == first_comment['id']
    # check we can't delete first comment
    response = superuser.delete(first_comment['url'] + '?comment=wow')
    assert response.status_code == 403
    # add comment by admin
    response = admin.post(
        thread['url'] + 'comments_page/', {
            'reply_id': first_comment['id'],
            'title': 'Im admin', 'body': 'my comment is awesome',
            'media': {},
        })
    assert response.status_code == 200
    data = response.json()
    assert len(data['comments']) == 2
    admin_comment = data['comments'][1]
    # check user can't delete it
    response = user.delete(admin_comment['url'] + '?comment=wow')
    assert response.status_code == 403
    # check user can't update it
    response = user.post(
        admin_comment['url'], {
            'reply_id': first_comment['id'],
            'title': 'hello world', 'body': 'world is great',
            'media': {},
        })
    assert response.status_code == 403
    # check comments readable by anonymous user
    response = client.get(thread['url'] + 'comments_page/')
    assert response.status_code == 200
    data = response.json()
    assert len(data['comments']) == 2
    # check we can't update first comment as comment
    response = admin.post(
        first_comment['url'], {
            'reply_id': first_comment['id'],
            'title': 'hello world', 'body': 'world is great',
            'media': {},
        })
    assert response.status_code == 403
    # check update comment preview
    response = admin.post(
        admin_comment['url'], {
            'reply_id': first_comment['id'],
            'title': 'hello world', 'body': 'world is great',
            'media': {}, 'preview': True
        })
    assert response.status_code == 200
    data = response.json()
    assert data['id'] == admin_comment['id']
    assert data['title'] == 'hello world'
    assert data['body'] == 'world is great'
    # check it is not really updated
    response = admin.get(admin_comment['url'])
    assert response.status_code == 200
    data = response.json()
    assert data['title'] == 'Im admin'
    assert data['body'] == 'my comment is awesome'
    # check we can't reply to comment in other thread
    response = admin.put(
        group['url'], {
            'title': 'thread2', 'body': 'thread2 description',
            'room': False, 'access_type': models.THREAD_ACCESS_TYPE_NOT_SET,
            'granted_rights': [], 'media': {}})
    assert response.status_code == 200
    thread2 = response.json()
    response = admin.post(
        thread['url'] + 'comments_page/', {
            'reply_id': thread2['first_comment_id'],
            'title': 'Im admin2', 'body': 'my comment is awesome2',
            'media': {},
        })
    assert response.status_code == 403
    # check comment without body is not added
    response = admin.post(
        thread['url'] + 'comments_page/', {
            'reply_id': thread['first_comment_id'],
            'title': 'Im admin2', 'body': '',
            'media': {},
        })
    assert response.status_code == 200
    data = response.json()
    assert len(data['comments']) == 2
