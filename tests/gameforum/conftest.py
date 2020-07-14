import io

import pytest
from PIL import Image, ImageDraw
from django.core.files import uploadedfile

from tulius.stories import models
from tulius.forum import models as forum_models
from tulius.gameforum import consts
from tulius.games import models as game_models


@pytest.fixture(name='image', scope='session')
def image_fixture():
    img = Image.new('RGB', (100, 30), color=(73, 109, 137))
    d = ImageDraw.Draw(img)
    d.text((10, 10), "Hello World", fill=(255, 255, 0))
    stream = io.BytesIO()
    img.save(stream, format='jpeg')
    stream.seek(0)
    return stream.read()


@pytest.fixture(name='story', scope='session')
def story_fixture(image, admin):
    obj = models.Story(
        name='Murder in tests',
        short_comment='Story for tests',
        creation_year=2020,
    )
    obj.save()
    obj.card_image.save(
        'card.jpg',
        uploadedfile.SimpleUploadedFile(
            "card.jpeg", image, content_type="image/jpeg"))
    obj.top_banner.save(
        'top_banner.jpg',
        uploadedfile.SimpleUploadedFile(
            "top_banner.jpeg", image, content_type="image/jpeg"))
    obj.bottom_banner.save(
        'bottom_banner.jpg',
        uploadedfile.SimpleUploadedFile(
            "bottom_banner.jpeg", image, content_type="image/jpeg"))
    obj.save()
    models.StoryAdmin(story=obj, user=admin.user).save()
    return obj


@pytest.fixture(name='story_detective', scope='session')
def story_detective_fixture(story, image):
    avatar = models.Avatar(story=story, name='Detective Smith')
    avatar.save()
    avatar.image.save(
        'detective.jpg',
        uploadedfile.SimpleUploadedFile(
            "detective.jpeg", image, content_type="image/jpeg"))
    avatar.save()
    obj = models.Character(
        story=story, name='Detective Smith', description='Public character',
        show_in_character_list=True, avatar=avatar)
    obj.save()
    return obj


@pytest.fixture(name='variation')
def variation_fixture(story):
    obj = models.Variation(story=story, name='Variation')
    obj.save()
    return obj


@pytest.fixture(name='variation_forum')
def variation_forum_fixture(variation, admin):
    thread = forum_models.Thread(
        parent=None, plugin_id=consts.GAME_FORUM_SITE_ID,
        user=admin.user, title=variation.name, body='', room=True)
    thread.save()
    variation.thread = thread
    variation.save()
    return variation.thread


@pytest.fixture(name='game')
def game_fixture(story, variation, admin):
    obj = game_models.Game(name='Game', variation=variation, serial_number=1)
    obj.save()
    variation.game = obj
    variation.save()
    game_models.GameAdmin(game=obj, user=admin.user).save()
    return obj


@pytest.fixture(name='game_guest_user', scope='session')
def game_guest_user_fixture(user_factory):
    return user_factory(username='Game Guest')


@pytest.fixture(name='game_guest')
def game_guest_fixture(game, game_guest_user):
    game_models.GameGuest(game=game, user=game_guest_user.user).save()
    return game_guest_user


@pytest.fixture(name='detective')
def detective_role_fixture(variation, user, story_detective):
    role = models.Role(
        variation=variation, character=story_detective, user=user.user,
        avatar=story_detective.avatar, name='Detective',
        show_in_character_list=True)
    role.save()
    return role


@pytest.fixture(name='murderer')
def murderer_fixture(variation):
    role = models.Role(
        variation=variation, character=None, user=None,
        avatar=None, name='Murderer',
        show_in_character_list=False)
    role.save()
    return role
