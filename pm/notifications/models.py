from django.dispatch import receiver
from pm.signals import *
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.sites.models import Site


@receiver(private_message_created)
def private_message_created_notification (sender, **kwargs):
    private_message = sender

    ctx_dict = {
        'private_message': private_message,
        'site': Site.objects.get(id=settings.SITE_ID)
    }

    subject = render_to_string('pm/notifications/message_created_subject.txt', ctx_dict)
    subject = ''.join(subject.splitlines())
    message = render_to_string('pm/notifications/message_created.txt', ctx_dict)
    private_message.receiver.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)