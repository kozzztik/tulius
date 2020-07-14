from django.db import transaction

from tulius.games import models as game_models


def test_marks_in_variation(variation, admin, detective):
    base_url = f'/api/game_forum/variation/{variation.id}/'
    # check no trust marks in variation
    response = admin.post(
        base_url + f'trust_mark/{detective.pk}/', {'value': 1})
    assert response.status_code == 403
    # check vote for not existing role
    response = admin.post(
        base_url + f'trust_mark/{detective.pk + 1}/', {'value': 1})
    assert response.status_code == 404


def test_marks_in_game(
        game, variation_forum, user, murderer, detective, game_guest, admin):
    game.status = game_models.GAME_STATUS_IN_PROGRESS
    with transaction.atomic():
        game.save()
    # Try to create thread without role specified. That is only for admins.
    base_url = f'/api/game_forum/variation/{game.variation.id}/'
    # check user can't vote for himself
    response = user.post(
        base_url + f'trust_mark/{detective.pk}/', {'value': 1})
    assert response.status_code == 403
    # check guests cant vote
    response = game_guest.post(
        base_url + f'trust_mark/{detective.pk}/', {'value': 1})
    assert response.status_code == 403
    # do votes
    response = user.post(
        base_url + f'trust_mark/{murderer.pk}/', {'value': -1})
    assert response.status_code == 200
    data = response.json()
    assert data['my_trust'] == 33
    assert data['trust_value'] == 33
    response = admin.post(
        base_url + f'trust_mark/{murderer.pk}/', {'value': 2})
    assert response.status_code == 200
    data = response.json()
    assert data['my_trust'] == 83
    assert data['trust_value'] == 58
    # check how it looks in variation
    response = admin.get(base_url)
    assert response.status_code == 200
    data = response.json()
    assert data['characters'][0]['id'] == murderer.pk
    assert data['characters'][0]['my_trust'] == 83
    assert data['characters'][0]['trust_value'] == 58
