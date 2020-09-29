import datetime

from django.conf import settings
from django.utils.timezone import now

from .models import LogMessage


def clear():
    time_clear = getattr(settings, 'LOGGER_MAX_AGE', 30 * 6)  # time in days
    time_delta = datetime.timedelta(days=time_clear)
    time_start = now() - time_delta
    objs = LogMessage.objects.filter(create_time__lt=time_start)
    return objs.delete()
