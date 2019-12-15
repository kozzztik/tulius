def clear():
    from .models import ProfilerMessage
    from django.conf import settings
    from django.utils.timezone import now
    import datetime
    time_clear = getattr(settings, 'PROFILER_MAX_AGE', 30 * 3) # time in days
    time_delta = datetime.timedelta(days=time_clear)
    timestart = now() - time_delta
    objs = ProfilerMessage.objects.filter(create_time__lt=timestart)
    count = objs.count()
    objs.delete()
    return count
