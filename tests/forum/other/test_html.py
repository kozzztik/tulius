def test_file_upload_protection(admin):
    response = admin.put(
        '/api/forum/uploaded_files/?file_name=1.js'
        '&content_type="application/javascript"', b"123",
        content_type='application/javascript; charset=utf-8')
    assert response.status_code == 403


def test_file_upload_works(superuser, client):
    response = superuser.put(
        '/api/forum/uploaded_files/?file_name=1.js'
        '&content_type="application/javascript"', b"123",
        content_type='application/javascript; charset=utf-8')
    assert response.status_code == 200
    data = response.json()
    assert data['file_name'] == '1.js'
    response = client.get(data['url'])
    assert response.status_code == 200
    assert b"".join(response.streaming_content) == b'123'
    response = superuser.get('/api/forum/uploaded_files/')
    assert response.status_code == 200
    data = response.json()
    assert len(data['files']) == 1
    assert data['files'][0]['file_name'] == '1.js'


def test_user_cant_set_html_on_comments(user, thread):
    response = user.post(
        thread['url'] + 'comments_page/', {
            'reply_id': thread['first_comment_id'],
            'title': 'foo', 'body': 'bar',
            'media': {'html': '<textarea></textarea>'},
        })
    assert response.status_code == 200
    data = response.json()
    assert len(data['comments']) == 2
    comment = data['comments'][1]
    assert comment['media'] == {}
    response = user.post(
        comment['url'], {
            'reply_id': thread['first_comment_id'],
            'title': 'bar', 'body': 'foo',
            'media': {'html': '<textarea></textarea>'},
        })
    assert response.status_code == 200
    data = response.json()
    assert data['title'] == 'bar'
    assert data['media'] == {}


def test_user_cant_set_html_on_threads(user, room_group):
    response=user.put(
        room_group['url'], {
            'title': 'thread', 'body': 'thread description',
            'room': False, 'access_type': 0, 'granted_rights': [],
            'media': {'html': '<textarea></textarea>'}})
    assert response.status_code == 200
    thread = response.json()
    assert thread['title'] == 'thread'
    assert thread['media'] == {}
    response = user.post(
        thread['url'], {
            'title': 'bar', 'body': 'foo',
            'media': {'html': '<textarea></textarea>'},
        })
    assert response.status_code == 200
    data = response.json()
    assert data['title'] == 'bar'
    assert data['media'] == {}


def test_html_media_on_threads(room_group, superuser):
    response=superuser.put(
        room_group['url'], {
            'title': 'thread', 'body': 'thread description',
            'room': False, 'access_type': 0, 'granted_rights': [],
            'important': False,
            'media': {'html': '<textarea></textarea>'}})
    assert response.status_code == 200
    thread = response.json()
    assert thread['title'] == 'thread'
    assert thread['media'] == {'html': '<textarea></textarea>'}
    response = superuser.post(
        thread['url'], {
            'title': 'bar', 'body': 'foo', 'important': False, 'closed': False,
            'media': {'html': '<input>'},
        })
    assert response.status_code == 200
    data = response.json()
    assert data['title'] == 'bar'
    assert data['media'] == {'html': '<input>'}
    response = superuser.post(
        thread['url'], {
            'title': 'bar', 'body': 'foo', 'important': False, 'closed': False,
            'media': {'html': ''},
        })
    assert response.status_code == 200
    data = response.json()
    assert data['title'] == 'bar'
    assert data['media'] == {}


def test_html_media_on_comments(superuser, thread):
    response = superuser.post(
        thread['url'] + 'comments_page/', {
            'reply_id': thread['first_comment_id'],
            'title': 'foo', 'body': 'bar',
            'media': {'html': '<textarea></textarea>'},
        })
    assert response.status_code == 200
    data = response.json()
    assert len(data['comments']) == 2
    comment = data['comments'][1]
    assert comment['media'] == {'html': '<textarea></textarea>'}
    response = superuser.post(
        comment['url'], {
            'reply_id': thread['first_comment_id'],
            'title': 'bar', 'body': 'foo',
            'media': {'html': '<input>'},
        })
    assert response.status_code == 200
    data = response.json()
    assert data['title'] == 'bar'
    assert data['media'] == {'html': '<input>'}
    response = superuser.post(
        comment['url'], {
            'reply_id': thread['first_comment_id'],
            'title': 'bar2', 'body': 'foo',
            'media': {'html': ''},
        })
    assert response.status_code == 200
    data = response.json()
    assert data['title'] == 'bar2'
    assert data['media'] == {}
