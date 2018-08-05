""" Looks like this module is not used yet."""
from django import dispatch
from django.template import loader
from django.conf import settings
from django.contrib.sites import models

from tulius.pm import signals


@dispatch.receiver(signals.private_message_created)
def private_message_created_notification(sender, **kwargs):
    private_message = sender

    ctx_dict = {
        'private_message': private_message,
        'site': models.Site.objects.get(id=settings.SITE_ID)
    }

    subject = loader.render_to_string(
        'pm/notifications/message_created_subject.txt', ctx_dict)
    subject = ''.join(subject.splitlines())
    message = loader.render_to_string(
        'pm/notifications/message_created.txt', ctx_dict)
    private_message.receiver.email_user(
        subject, message, settings.DEFAULT_FROM_EMAIL)
