def clear():
    from .models import LogMessage
    from django.conf import settings
    from django.utils.timezone import now
    import datetime
    time_clear = getattr(settings, 'LOGGER_MAX_AGE', 30 * 6) # time in days
    time_delta = datetime.timedelta(days=time_clear)
    timestart = now() - time_delta
    objs = LogMessage.objects.filter(create_time__lt=timestart)
    return objs.delete()