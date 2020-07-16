import io

from PIL import Image, ImageDraw


def test_images_media_upload(user, client):
    img = Image.new('RGB', (100, 30), color=(73, 109, 137))
    d = ImageDraw.Draw(img)
    d.text((10, 10), "Hello World", fill=(255, 255, 0))
    stream = io.BytesIO()
    img.save(stream, format='jpeg')
    stream.seek(0)
    data = stream.read()
    # check anonymous user cant upload files
    response = client.put(
        '/api/forum/images/?file_name=foo.jpg'
        '&content_type="image/jpeg"', data,
        content_type='image/jpeg; charset=utf-8')
    assert response.status_code == 403
    # check logged in user can upload
    response = user.put(
        '/api/forum/images/?file_name=foo.jpg'
        '&content_type="image/jpeg"', data,
        content_type='image/jpeg; charset=utf-8')
    assert response.status_code == 200
    data = response.json()
    # check that we can retrieve image and thumb
    response = client.get(data['url'])
    assert response.status_code == 200
    response = client.get(data['thumb'])
    assert response.status_code == 200


def test_images_media_on_thread(user, room_group):
    response = user.get('/api/forum/images/')
    assert response.status_code == 200
    data = response.json()
    assert len(data['images']) > 0
    image = data['images'][0]
    # check we can create thread with images
    response = user.put(
        room_group['url'], {
            'title': 'thread', 'body': 'thread description',
            'room': False, 'access_type': 0, 'granted_rights': [],
            'media': {'images': [
                {'id': image['id'], 'foo': 'bar'},
                {'id': image['id'], 'bar': 'foo'},
            ]}})
    assert response.status_code == 200
    thread = response.json()
    assert thread['title'] == 'thread'
    assert 'images' in thread['media']
    assert len(thread['media']['images']) == 2
    assert thread['media']['images'][0] == image
    assert thread['media']['images'][1] == image
    # check we can add images
    response = user.post(
        thread['url'], {
            'title': 'bar', 'body': 'foo',
            'media': {'images': [
                {'id': image['id'], 'foo': 'bar'},
                {'id': image['id'], 'bar': 'foo'},
                {'id': image['id'], 'bar': 'foo'},
            ]}
        })
    assert response.status_code == 200
    thread = response.json()
    assert 'images' in thread['media']
    assert len(thread['media']['images']) == 3
    assert thread['media']['images'][0] == image
    assert thread['media']['images'][1] == image
    assert thread['media']['images'][2] == image
    # check we can delete images
    response = user.post(
        thread['url'], {
            'title': 'bar', 'body': 'foo',
            'media': {'images': [
                {'id': image['id'], 'foo': 'bar'},
            ]}
        })
    assert response.status_code == 200
    thread = response.json()
    assert 'images' in thread['media']
    assert len(thread['media']['images']) == 1
    assert thread['media']['images'][0] == image
    response = user.post(
        thread['url'], {
            'title': 'bar', 'body': 'foo',
            'media': {'images': []}
        })
    assert response.status_code == 200
    thread = response.json()
    assert thread['media'] == {}


def test_images_media_on_comments(user, thread):
    response = user.get('/api/forum/images/')
    assert response.status_code == 200
    data = response.json()
    assert len(data['images']) > 0
    image = data['images'][0]
    # check we can create thread with images
    response = user.post(
        thread['url'] + 'comments_page/', {
            'reply_id': thread['first_comment_id'],
            'title': 'thread', 'body': 'thread description',
            'media': {'images': [
                {'id': image['id'], 'foo': 'bar'},
                {'id': image['id'], 'bar': 'foo'},
            ]}})
    assert response.status_code == 200
    data = response.json()
    assert len(data['comments']) == 2
    comment = data['comments'][1]
    assert comment['title'] == 'thread'
    assert 'images' in comment['media']
    assert len(comment['media']['images']) == 2
    assert comment['media']['images'][0] == image
    assert comment['media']['images'][1] == image
    # check we can add images
    response = user.post(
        comment['url'], {
            'reply_id': thread['first_comment_id'],
            'title': 'bar', 'body': 'foo',
            'media': {'images': [
                {'id': image['id'], 'foo': 'bar'},
                {'id': image['id'], 'bar': 'foo'},
                {'id': image['id'], 'bar': 'foo'},
            ]}
        })
    assert response.status_code == 200
    data = response.json()
    assert 'images' in data['media']
    assert len(data['media']['images']) == 3
    assert data['media']['images'][0] == image
    assert data['media']['images'][1] == image
    assert data['media']['images'][2] == image
    # check we can delete images
    response = user.post(
        comment['url'], {
            'reply_id': thread['first_comment_id'],
            'title': 'bar', 'body': 'foo',
            'media': {'images': [
                {'id': image['id'], 'foo': 'bar'},
            ]}
        })
    assert response.status_code == 200
    data = response.json()
    assert 'images' in data['media']
    assert len(data['media']['images']) == 1
    assert data['media']['images'][0] == image
    response = user.post(
        comment['url'], {
            'reply_id': thread['first_comment_id'],
            'title': 'bar', 'body': 'foo',
            'media': {'images': []}
        })
    assert response.status_code == 200
    data = response.json()
    assert data['media'] == {}
