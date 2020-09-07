import os
import datetime

from django.core.mail.backends import base
from django.conf import settings


class EmailBackend(base.BaseEmailBackend):
    def __init__(self, fail_silently=False, **kwargs):
        super(EmailBackend, self).__init__(
            fail_silently=fail_silently, **kwargs)
        self.base_dir = settings.EMAIL_FILE_PATH

    def write_message(self, receiver, message):
        msg = message.message()
        path = os.path.join(self.base_dir, receiver)
        os.makedirs(path, exist_ok=True)
        file_name = os.path.join(
            path, str(datetime.datetime.now().timestamp()))
        f = open(file_name, 'ab')
        try:
            f.write(msg.as_bytes())
        finally:
            f.close()

    def send_messages(self, email_messages):
        msg_count = 0
        try:
            for message in email_messages:
                for receiver in message.to:
                    self.write_message(receiver, message)
                    msg_count += 1
        except Exception:
            if not self.fail_silently:
                raise
        return msg_count
