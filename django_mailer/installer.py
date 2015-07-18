def clear():
    from .models import Message
    from django.conf import settings
    from django.utils.timezone import now
    import datetime
    time_clear = getattr(settings, 'MAILER_MAX_AGE', 30 * 6) # time in days
    time_delta = datetime.timedelta(days=time_clear)
    timestart = now() - time_delta
    objs = Message.objects.filter(date_created__lt=timestart)
    return objs.delete()