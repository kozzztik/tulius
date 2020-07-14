import pytest
from django.core.files import uploadedfile
from django.db import transaction

from tulius.stories import models
from tulius.games import models as game_models


@pytest.fixture(name='story_material', scope='session')
def story_material_fixture(story):
    obj = models.AdditionalMaterial(
        story=story, name='Misc information',
        body='Misc info about story for users', admins_only=False)
    obj.save()
    return obj


@pytest.fixture(name='story_hidden_material', scope='session')
def story_hidden_material_fixture(story):
    obj = models.AdditionalMaterial(
        story=story, name='Hidden info',
        body='Info hidden from users', admins_only=True)
    obj.save()
    return obj


@pytest.fixture(name='story_illustration', scope='session')
def story_illustration_fixture(story, image):
    obj = models.Illustration(
        story=story, name='Map of location', admins_only=False)
    obj.save()
    obj.image.save(
        'image.jpg',
        uploadedfile.SimpleUploadedFile(
            "image.jpeg", image, content_type="image/jpeg"))
    obj.save()
    return obj


@pytest.fixture(name='story_hidden_illustration', scope='session')
def story_hidden_illustration_fixture(story, image):
    obj = models.Illustration(
        story=story, name='Map of treasures', admins_only=True)
    obj.save()
    obj.image.save(
        'image.jpg',
        uploadedfile.SimpleUploadedFile(
            "image.jpeg", image, content_type="image/jpeg"))
    obj.save()
    return obj


@pytest.fixture(name='story_materials', scope='session')
def story_materials_fixture(
        story_material, story_hidden_material, story_illustration,
        story_hidden_illustration):
    return [
        story_material, story_hidden_material, story_illustration,
        story_hidden_illustration]


@pytest.fixture(name='variation_material')
def variation_material_fixture(story, variation):
    obj = models.AdditionalMaterial(
        story=story, variation=variation, name='Misc info about variation',
        body='Misc info for users', admins_only=False)
    obj.save()
    return obj


@pytest.fixture(name='variation_hidden_material')
def variation_hidden_material_fixture(story, variation):
    obj = models.AdditionalMaterial(
        story=story, variation=variation, name='Hidden in variation',
        body='Info hidden from users', admins_only=True)
    obj.save()
    return obj


@pytest.fixture(name='variation_illustration')
def variation_illustration_fixture(story, variation, image):
    obj = models.Illustration(
        story=story, variation=variation, name='Map of location',
        admins_only=False)
    obj.save()
    obj.image.save(
        'image.jpg',
        uploadedfile.SimpleUploadedFile(
            "image.jpeg", image, content_type="image/jpeg"))
    obj.save()
    return obj


@pytest.fixture(name='variation_hidden_illustration')
def variation_hidden_illustration_fixture(story, variation, image):
    obj = models.Illustration(
        story=story, variation=variation, name='Map of treasures',
        admins_only=True)
    obj.save()
    obj.image.save(
        'image.jpg',
        uploadedfile.SimpleUploadedFile(
            "image.jpeg", image, content_type="image/jpeg"))
    obj.save()
    return obj


@pytest.fixture(name='variation_materials')
def variation_materials_fixture(
        variation_material, variation_hidden_material, variation_illustration,
        variation_hidden_illustration):
    return [
        variation_material, variation_hidden_material, variation_illustration,
        variation_hidden_illustration]


def test_variation_view(
        variation, client, admin, user, superuser, variation_materials,
        story_materials):
    # check only admins have access to variation
    response = client.get(f'/api/game_forum/variation/{variation.id}/')
    assert response.status_code == 403
    response = user.get(f'/api/game_forum/variation/{variation.id}/')
    assert response.status_code == 403
    response = superuser.get(f'/api/game_forum/variation/{variation.id}/')
    assert response.status_code == 200
    response = admin.get(f'/api/game_forum/variation/{variation.id}/')
    assert response.status_code == 200
    data = response.json()
    assert len(data['materials']) == 4
    assert len(data['illustrations']) == 4


@pytest.mark.parametrize('status', [
    game_models.GAME_STATUS_NEW,
    game_models.GAME_STATUS_OPEN_FOR_REGISTRATION,
    game_models.GAME_STATUS_REGISTRATION_COMPLETED])
def test_game_variation_view_not_started(
        client, admin, user, superuser, variation_materials, story_materials,
        game, status, game_guest, detective, murderer):
    game.status = status
    with transaction.atomic():
        game.save()
    # check only admins have access to game variation when it is not started
    response = client.get(f'/api/game_forum/variation/{game.variation.id}/')
    assert response.status_code == 403
    response = user.get(f'/api/game_forum/variation/{game.variation.id}/')
    assert response.status_code == 403
    response = superuser.get(f'/api/game_forum/variation/{game.variation.id}/')
    assert response.status_code == 200
    response = admin.get(f'/api/game_forum/variation/{game.variation.id}/')
    assert response.status_code == 200
    data = response.json()
    assert len(data['materials']) == 4
    assert len(data['illustrations']) == 4
    assert len(data['characters']) == 2
    assert len(data['roles']) == 2
    assert data['write_right']
    # Guests have access too
    response = game_guest.get(
        f'/api/game_forum/variation/{game.variation.id}/')
    assert response.status_code == 200
    data = response.json()
    assert len(data['materials']) == 2
    assert len(data['illustrations']) == 2
    assert len(data['characters']) == 1
    assert len(data['roles']) == 0
    assert not data['write_right']


def test_game_variation_view_in_progress(
        client, user, variation_materials, story_materials,
        game, detective, murderer):
    game.status = game_models.GAME_STATUS_IN_PROGRESS
    with transaction.atomic():
        game.save()
    # check anonymous still can't access game
    response = client.get(f'/api/game_forum/variation/{game.variation.id}/')
    assert response.status_code == 403
    # check user access
    response = user.get(f'/api/game_forum/variation/{game.variation.id}/')
    assert response.status_code == 200
    data = response.json()
    assert len(data['materials']) == 2
    assert len(data['illustrations']) == 2
    assert len(data['characters']) == 1
    assert data['characters'][0]['id'] == detective.pk
    assert len(data['roles']) == 1
    assert data['roles'][0]['id'] == detective.pk
    assert data['write_right']


def test_game_variation_view_opened(
        client, user, variation_materials, story_materials,
        game, detective, murderer):
    game.status = game_models.GAME_STATUS_COMPLETED_OPEN
    with transaction.atomic():
        game.save()
    # check anonymous still can't access game
    response = client.get(f'/api/game_forum/variation/{game.variation.id}/')
    assert response.status_code == 200
    data = response.json()
    assert len(data['materials']) == 2
    assert len(data['illustrations']) == 2
    assert len(data['characters']) == 1
    assert data['characters'][0]['id'] == detective.pk
    assert len(data['roles']) == 1
    assert data['roles'][0]['id'] == detective.pk
    assert not data['write_right']


def test_redirect_api(variation, variation_forum, admin, client):
    response = client.get(
        f'/api/game_forum/thread_redirrect/{variation_forum.id}/')
    assert response.status_code == 200
    data = response.json()
    assert data['variation_id'] == variation.pk
    assert data['room']
    # create a thread
    base_url = f'/api/game_forum/variation/{variation.id}/'
    response = admin.put(
        base_url + f'thread/{variation_forum.id}/', {
            'title': 'thread', 'body': 'thread description',
            'room': False, 'access_type': 0, 'granted_rights': [],
            'important': False, 'media': {}})
    assert response.status_code == 200
    thread = response.json()
    # check redirect
    response = client.get(
        f'/api/game_forum/thread_redirrect/{thread["id"]}/')
    assert response.status_code == 200
    data = response.json()
    assert data['variation_id'] == variation.pk
    assert not data['room']
