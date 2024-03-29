import datetime

from django.conf import settings
from django.db import models
from django.template.loader import render_to_string
from django.utils.timezone import now as datetime_now
from django.utils.translation import gettext_lazy as _


class RegistrationProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, models.PROTECT,
        verbose_name=_('user'))
    activation_key = models.CharField(_('activation key'), max_length=40)
    ACTIVATED = "ALREADY_ACTIVATED"

    class Meta:
        verbose_name = _('registration profile')
        verbose_name_plural = _('registration profiles')

    def __str__(self):
        return "Registration information for %s" % self.user

    def activation_key_expired(self):
        expiration_date = datetime.timedelta(
            days=settings.ACCOUNT_ACTIVATION_DAYS)
        if self.activation_key == self.ACTIVATED:
            return True
        return self.user.date_joined + expiration_date <= datetime_now()

    def send_activation_email(self, site):
        ctx_dict = {'activation_key': self.activation_key,
                    'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
                    'site': site}
        subject = render_to_string('login/activation_email_subject.txt',
                                   ctx_dict)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())

        message = render_to_string('login/activation_email.haml',
                                   ctx_dict)

        self.user.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)
