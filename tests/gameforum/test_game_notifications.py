from unittest import mock
from django.db import transaction
from django.core import mail

from tulius.events import models
from tulius.games import models as game_models


def test_game_open_for_registration_notification(game, admin):
    models.Notification(
        code_name='game_open_for_registration',
        header_template='{{ game.name }} opened for registration',
        body_template='{{ game.get_absolute_url }}',
    ).save()
    game.status = game_models.GAME_STATUS_OPEN_FOR_REGISTRATION
    with transaction.atomic():
        game.save()
    assert mail.outbox[0].subject == 'Game opened for registration'
    assert mail.outbox[0].body == game.get_absolute_url()


def test_notification_bad_template(game, admin):
    models.Notification(
        code_name='game_open_for_registration',
        header_template='{{ foo|bar }} opened for registration',
        body_template='{{ game.get_absolute_url }}',
    ).save()
    game.status = game_models.GAME_STATUS_OPEN_FOR_REGISTRATION
    with transaction.atomic():
        game.save()
    assert mail.outbox == []


def test_notification_with_broken_rendering(game, admin):
    models.Notification(
        code_name='game_open_for_registration',
        header_template='{{ game.name }} opened for registration',
        body_template='{{ game.get_absolute_url }}',
    ).save()
    game.status = game_models.GAME_STATUS_OPEN_FOR_REGISTRATION
    template = mock.MagicMock()
    template.render.side_effect = Exception('foo')
    with mock.patch('django.template.Template', return_value=template):
        with transaction.atomic():
            game.save()
    assert template.render.called
    assert mail.outbox == []


def test_registration_completed_notification(game, admin, user, detective):
    game_models.RoleRequest(game=game, user=user.user).save()
    models.Notification(
        code_name='game_registration_completed',
        header_template='{{ game.name }} registration completed',
        body_template='{{ game.get_absolute_url }}',
    ).save()
    game.status = game_models.GAME_STATUS_REGISTRATION_COMPLETED
    with transaction.atomic():
        game.save()
    assert len(mail.outbox) == 1  # only user with request received email
    assert mail.outbox[0].subject == 'Game registration completed'
    assert mail.outbox[0].body == game.get_absolute_url()
    assert mail.outbox[0].to == [user.user.email]


def test_game_started_notification(game, user, detective):
    models.Notification(
        code_name='game_in_progress',
        header_template='{{ game.name }} in progress',
        body_template='{{ game.get_absolute_url }}',
    ).save()
    game.status = game_models.GAME_STATUS_IN_PROGRESS
    with transaction.atomic():
        game.save()
    assert len(mail.outbox) == 1  # only user with request received email
    assert mail.outbox[0].subject == 'Game in progress'
    assert mail.outbox[0].body == game.get_absolute_url()
    assert mail.outbox[0].to == [user.user.email]


def teardown_function():
    models.Notification.objects.all().delete()
    mail.outbox = []
