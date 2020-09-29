from tulius.games import signals
from tulius.events import tasks
from tulius.games import models


def game_status_changed_dispatcher(sender, **kwargs):
    new_status = kwargs['new_status']
    if new_status == models.GAME_STATUS_OPEN_FOR_REGISTRATION:
        tasks.game_open_for_registration.apply_async(args=[sender.pk])
    elif new_status == models.GAME_STATUS_REGISTRATION_COMPLETED:
        tasks.game_registration_completed.apply_async(args=[sender.pk])
    elif new_status == models.GAME_STATUS_IN_PROGRESS:
        tasks.game_in_progress.apply_async(args=[sender.pk])


def init():
    signals.game_status_changed.connect(game_status_changed_dispatcher)
