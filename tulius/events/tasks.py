import logging

from celery import shared_task
from django import template
from django.conf import settings
from django.core.mail import EmailMessage

from tulius import models as tulius_models
from tulius.events import models as events_models
from tulius.games import models as games_models
from tulius.stories import models as stories_models

logger = logging.getLogger('django.request')


def send_notifications(users, notification_id, variables):
    notification = events_models.Notification.objects.get_or_create(
        code_name=notification_id)[0]
    if (not notification.body_template) or (not notification.header_template):
        return
    try:
        header_template = template.Template(notification.header_template)
        body_template = template.Template(notification.body_template)
    except Exception as e:
        logger.error(
            'Can`t send email notification %s, template not loaded.',
            notification.id)
        logger.error(e)
        return
    user_notifications = events_models.UserNotification.objects.filter(
        notification=notification, enabled=False)
    excluded_users_ids = [item.user_id for item in user_notifications]
    users = [user for user in users if user.id not in excluded_users_ids]
    context_variables = {}
    for user in users:
        try:
            context_variables.clear()
            context_variables = variables.copy()
            context_variables['user'] = user
            context = template.Context(context_variables)
            header = header_template.render(context)
            body = body_template.render(context)
            msg = EmailMessage(
                header, body, settings.DEFAULT_FROM_EMAIL, [user.email])
            msg.content_subtype = "html"
            msg.send()
        except Exception as e:
            logger.error(
                'Can`t send email notification %s to %s',
                notification.id, user.id)
            logger.error(e)


@shared_task(track_started=True)
def game_open_for_registration(game_id):
    variables = {'game': games_models.Game.objects.get(pk=game_id)}
    users = tulius_models.User.objects.filter(is_active=True)
    send_notifications(users, 'game_open_for_registration', variables)


@shared_task(track_started=True)
def game_registration_completed(game_id):
    game = games_models.Game.objects.get(pk=game_id)
    requests = games_models.RoleRequest.objects.filter(game=game)
    users = [request.user for request in requests]
    for user in users:
        user.assigned_roles = []
    roles = stories_models.Role.objects.filter(
        variation=game.variation, deleted=False)
    for role in roles:
        for user in users:
            if role.user_id == user.id:
                user.assigned_roles = user.assigned_roles + [role]
    send_notifications(users, 'game_registration_completed', {'game': game})


@shared_task(track_started=True)
def game_in_progress(game_id):
    game = games_models.Game.objects.get(pk=game_id)
    roles = stories_models.Role.objects.filter(
        variation=game.variation, deleted=False)
    users_dict = {}
    for role in roles:
        if role.user:
            users_dict[role.user_id] = role.user
    users = users_dict.values()
    for user in users:
        user.assigned_roles = []
    for role in roles:
        for user in users:
            if role.user_id == user.id:
                user.assigned_roles = user.assigned_roles + [role]
    send_notifications(users, 'game_in_progress', {'game': game})
