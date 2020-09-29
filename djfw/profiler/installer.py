import datetime

from django.conf import settings
from django.utils.timezone import now

from .models import ProfilerMessage


def clear():
    time_clear = getattr(settings, 'PROFILER_MAX_AGE', 30 * 3)  # time in days
    time_delta = datetime.timedelta(days=time_clear)
    time_start = now() - time_delta
    objs = ProfilerMessage.objects.filter(create_time__lt=time_start)
    count = objs.count()
    objs.delete()
    return count
