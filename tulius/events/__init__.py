from django.template import loader, Context
from django.conf import settings
from django.core.mail import EmailMessage
from tulius.games.signals import game_status_changed
import logging

logger = logging.getLogger('django.request')


def reencode(a):
    import types
    if isinstance(a, types.StringType):
        a = a.decode('utf8')
    return a


def send_notifications(users, notification_id, varibles):
    from .models import Notification, UserNotification
    notification = Notification.objects.get_or_create(
        code_name=notification_id)[0]
    if (not notification.body_template) or (not notification.header_template):
        return
    try:
        
        header_template = loader.get_template_from_string(
            reencode(notification.header_template))
        body_template = loader.get_template_from_string(
            reencode(notification.body_template))
    except Exception as e:
        logger.error(
            'Can`t send email notification %s, template not loaded.' % (
                notification.id))
        logger.error(e)
    user_notifications = UserNotification.objects.filter(
        notification=notification, enabled=False)
    excluded_users_ids = [item.user_id for item in user_notifications]
    users = [user for user in users if (user.id not in excluded_users_ids)]
    context_varibles = {}
    for user in users:
        try:
            context_varibles.clear()
            context_varibles = varibles.copy()
            context_varibles['user'] = user
            context = Context(context_varibles)
            header = header_template.render(context)
            body = body_template.render(context)
            msg = EmailMessage(
                header, body, settings.DEFAULT_FROM_EMAIL, [user.email])
            msg.content_subtype = "html"
            msg.send()
        except Exception as e:
            logger.error(
                'Can`t send email notification %s to %s' % (
                    notification.id, user.id))
            logger.error(e)


def game_open_for_registration(game, varibles):
    from tulius.models import User
    users = User.objects.filter(is_active=True)
    send_notifications(users, 'game_open_for_registration', varibles)


def game_registration_completed(game, varibles):
    from tulius.games.models import RoleRequest
    from tulius.stories.models import Role
    requests = RoleRequest.objects.filter(game=game)
    users = [request.user for request in requests]
    for user in users:
        user.assigned_roles = []
    roles = Role.objects.filter(variation=game.variation, deleted=False)
    for role in roles:
        for user in users:
            if role.user_id == user.id:
                user.assigned_roles = user.assigned_roles + [role]
    send_notifications(users, 'game_registration_completed', varibles)


def game_in_progress(game, varibles):
    from tulius.stories.models import Role
    roles = Role.objects.filter(variation=game.variation, deleted=False)
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
    send_notifications(users, 'game_in_progress', varibles)


def game_status_changed_dispatcher(sender, **kwargs):
    from tulius.games import models
    new_status = kwargs['new_status']
    varibles = {}
    varibles['game'] = sender
    if new_status == models.GAME_STATUS_OPEN_FOR_REGISTRATION:
        game_open_for_registration(sender, varibles)
    elif new_status == models.GAME_STATUS_REGISTRATION_COMPLETED:
        game_registration_completed(sender, varibles)
    elif new_status == models.GAME_STATUS_IN_PROGRESS:
        game_in_progress(sender, varibles)


game_status_changed.connect(game_status_changed_dispatcher)
