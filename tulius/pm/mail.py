import logging

from tulius.models import User
from tulius.pm.models import PrivateMessage


logger = logging.getLogger('django.request')


def get_mail(mail):
    receiver = mail.recipient_mail
    if not receiver.find('@tulius.com'):
        return False
    receiver = receiver.replace('@tulius.com', '')
    get_by_id = False
    try:
        receiver = int(receiver)
        get_by_id = True
    except:
        pass
    try:
        if get_by_id:
            receiver = User.objects.get(id=receiver, is_active=True)
        else:
            receiver = User.objects.get(username=receiver, is_active=True)
    except User.DoesNotExist:
        logger.warning(
            'Email not received. Recipient %s not found', receiver)
        return True
    try:
        sender = User.objects.get(email=mail.sender_mail, is_active=True)
    except User.DoesNotExist:
        logger.warning(
            'Email not received. Sender %s not found', mail.sender_mail)
        return True

    body = mail.body.replace('\\n', '\n').strip(' \n').replace('\n', '\t\n')
    PrivateMessage(sender=sender, receiver=receiver, body=body).save()
    return True
