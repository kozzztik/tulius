from django.db import transaction

from tulius.stories import models as stories_models
from tulius.games import models as game_models


def test_fix_game_counters(game, variation_forum, user, detective, superuser):
    game.status = game_models.GAME_STATUS_IN_PROGRESS
    with transaction.atomic():
        game.save()
    # create thread with "no read" and no role
    base_url = f'/api/game_forum/variation/{game.variation.id}/'
    response = user.put(
        base_url + f'thread/{variation_forum.id}/', {
            'title': 'thread', 'body': 'thread description',
            'room': False, 'access_type': 0, 'role_id': detective.pk,
            'granted_rights': [], 'important': False, 'media': {}})
    assert response.status_code == 200
    obj = stories_models.Role.objects.get(pk=detective.pk)
    assert obj.comments_count == 1
    obj.comments_count = 0
    obj.save()
    # do fix
    response = superuser.post(base_url + f'thread/{variation_forum.pk}/fix/')
    assert response.status_code == 200
    # check
    obj = stories_models.Role.objects.get(pk=detective.pk)
    assert obj.comments_count == 1
