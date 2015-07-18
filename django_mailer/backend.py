from django.core.mail.backends.base import BaseEmailBackend

from django_mailer import queue_email_message


class DbBackend(BaseEmailBackend):
    
    def send_messages(self, email_messages):
        num_sent = 0
        for email in email_messages:
            queue_email_message(email)
            num_sent += 1
        return num_sent