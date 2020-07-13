import io

from PIL import Image, ImageDraw
from django.core.files import uploadedfile
from django.test import client as test_client
import pytest

from djfw.wysibb import models


@pytest.fixture(name='image', scope='session')
def image_fixture():
    img = Image.new('RGB', (100, 30), color=(73, 109, 137))
    d = ImageDraw.Draw(img)
    d.text((10, 10), "Hello World", fill=(255, 255, 0))
    stream = io.BytesIO()
    img.save(stream, format='jpeg')
    stream.seek(0)
    return stream.read()


def test_images(client, user, image):
    # check "get" not works for anonymous user
    response = client.get('/api/ckeditor/images/')
    assert response.status_code == 403
    # check works for registered user
    response = user.get('/api/ckeditor/images/')
    assert response.status_code == 200
    data = response.json()
    assert data == {}
    # Prepare image
    upload = uploadedfile.SimpleUploadedFile(
        "file.jpeg", image, content_type="image/jpeg")
    dj_client = test_client.Client()
    # check anonymous user cant upload files
    response = dj_client.post('/api/ckeditor/images/', {'upload': upload})
    assert response.status_code == 403
    # login & upload
    dj_client.login(username=user.user.username, password=user.user.username)
    upload = uploadedfile.SimpleUploadedFile(
        "file.jpeg", image, content_type="image/jpeg")
    response = dj_client.post('/api/ckeditor/images/', {'upload': upload})
    assert response.status_code == 200
    data = response.json()
    # check we can load it by url
    response = client.get(data['url'])
    assert response.status_code == 200


def test_smiles(client, image):
    # make a smile
    smile = models.Smile(name='lol', text=':lol:')
    smile.save()
    smile.image.save(
        'smile.jpg',
        uploadedfile.SimpleUploadedFile(
            "file.jpeg", image, content_type="image/jpeg"))
    smile.save()
    # get it
    response = client.get('/api/ckeditor/smiles/')
    assert response.status_code == 200
    data = response.json()
    assert data['smiles'][0]['text'] == ':lol:'
    url = data['base_url'] + data['smiles'][0]['file_name']
    response = client.get(url)
    assert response.status_code == 200
