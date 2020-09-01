def test_youtube_media_on_threads(room_group, user):
    response=user.put(
        room_group['url'], {
            'title': 'thread', 'body': 'thread description',
            'room': False, 'default_rights': None, 'granted_rights': [],
            'important': False,
            'media': {'youtube': 'sp_lN9FNjGs'}})
    assert response.status_code == 200
    thread = response.json()
    assert thread['title'] == 'thread'
    assert thread['media'] == {'youtube': 'sp_lN9FNjGs'}
    response = user.post(
        thread['url'], {
            'title': 'bar', 'body': 'foo', 'important': False, 'closed': False,
            'media': {'youtube': 'ocYxTG8w8wM'},
        })
    assert response.status_code == 200
    data = response.json()
    assert data['title'] == 'bar'
    assert data['media'] == {'youtube': 'ocYxTG8w8wM'}
    response = user.post(
        thread['url'], {
            'title': 'bar', 'body': 'foo', 'important': False, 'closed': False,
            'media': {'youtube': ''},
        })
    assert response.status_code == 200
    data = response.json()
    assert data['title'] == 'bar'
    assert data['media'] == {}


def test_youtube_media_on_comments(user, thread):
    response = user.post(
        thread['url'] + 'comments_page/', {
            'reply_id': thread['first_comment_id'],
            'title': 'foo', 'body': 'bar',
            'media': {'youtube': 'sp_lN9FNjGs'},
        })
    assert response.status_code == 200
    data = response.json()
    assert len(data['comments']) == 2
    comment = data['comments'][1]
    assert comment['media'] == {'youtube': 'sp_lN9FNjGs'}
    response = user.post(
        comment['url'], {
            'reply_id': thread['first_comment_id'],
            'title': 'bar', 'body': 'foo',
            'media': {'youtube': 'ocYxTG8w8wM'},
        })
    assert response.status_code == 200
    data = response.json()
    assert data['title'] == 'bar'
    assert data['media'] == {'youtube': 'ocYxTG8w8wM'}
    response = user.post(
        comment['url'], {
            'reply_id': thread['first_comment_id'],
            'title': 'bar2', 'body': 'foo',
            'media': {'youtube': ''},
        })
    assert response.status_code == 200
    data = response.json()
    assert data['title'] == 'bar2'
    assert data['media'] == {}
