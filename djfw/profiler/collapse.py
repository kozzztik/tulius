import datetime
import json

from django.db.models import Min, Max
from django.utils.timezone import get_current_timezone

from .models import ProfilerMessage, ClientCollapse, TimeCollapse

COLLAPSE_INTERVALS = 24 * 2  # intervals in day, 30 minutes


# pylint: disable=too-many-branches,too-many-statements
def do_collapse(day):
    if not day:
        query = ProfilerMessage.objects.aggregate(
            time_min=Min('create_time'), time_max=Max('create_time'))
        max_time = query['time_max'].date()
        min_time = query['time_min'].date()
        timedelta = max_time - min_time
        ClientCollapse.objects.all().delete()
        TimeCollapse.objects.all().delete()
        dates = (
            (min_time + datetime.timedelta(days=x))
            for x in range(timedelta.days))
        for x in dates:
            do_collapse(x)
        return
    day_start = datetime.datetime(
        day.year, day.month, day.day, tzinfo=get_current_timezone())
    ClientCollapse.objects.filter(day=day_start).delete()
    TimeCollapse.objects.filter(day=day_start).delete()
    client_stats = ClientCollapse(day=day_start)
    oses = {}
    browsers = {}
    devices = {}
    modules = {}
    for x in range(COLLAPSE_INTERVALS):
        min_time = day_start + datetime.timedelta(minutes=x * 30)
        max_time = day_start + datetime.timedelta(minutes=(x + 1) * 30)
        messages = ProfilerMessage.objects.filter(
            create_time__gte=min_time, create_time__lt=max_time)
        time_stats = TimeCollapse(day=day_start, create_time=min_time)
        time_stats.calls_count = 0
        time_stats.anon_calls_count = 0
        time_stats.exec_time = 0
        time_stats.db_time = 0
        time_stats.db_count = 0
        time_stats.template_time = 0
        time_stats.template_db_time = 0
        time_stats.template_db_count = 0
        time_stats.exceptions_count = 0
        time_stats.mobiles_count = 0
        for message in messages:
            time_stats.calls_count += 1
            if not message.user_id:
                time_stats.anon_calls_count += 1
            time_stats.exec_time += message.exec_time
            time_stats.db_time += message.db_time
            time_stats.db_count += message.db_count
            time_stats.template_time += message.template_time
            time_stats.template_db_time += message.template_db_time
            time_stats.template_db_count += message.template_db_count
            if message.error:
                time_stats.exceptions_count += 1
            if message.mobile:
                time_stats.mobiles_count += 1
            if message.device:
                if message.device not in devices:
                    devices[message.device] = 0
                devices[message.device] += 1
            os = message.os
            os_version = message.os_version or '-'
            if os not in oses:
                oses[os] = {}
            if os_version not in oses[os]:
                oses[os][os_version] = 0
            oses[os][os_version] += 1
            browser = message.browser
            browser_version = message.browser_version or '-'
            if browser not in browsers:
                browsers[browser] = {}
            if browser_version not in browsers[browser]:
                browsers[browser][browser_version] = 0
            browsers[browser][browser_version] += 1
            module = message.module_name
            func = message.func_name or '-'
            if module not in modules:
                modules[module] = {}
            if func not in modules[module]:
                modules[module][func] = {
                    'calls': 0, 'exec': 0, 'db_count': 0,
                    'db_time': 0, 'render': 0, 'exceptions': 0, 'mobiles': 0,
                    'anons': 0}
            modules[module][func]['calls'] += 1
            modules[module][func]['exec'] += message.exec_time
            modules[module][func]['db_count'] += message.db_count
            modules[module][func]['db_time'] += message.db_time
            modules[module][func]['render'] += message.template_time
            if message.error:
                modules[module][func]['exceptions'] += 1
            if message.mobile:
                modules[module][func]['mobiles'] += 1
            if not message.user_id:
                modules[module][func]['anons'] += 1
        time_stats.save()
    client_stats.browsers = json.dumps(browsers)
    client_stats.oses = json.dumps(oses)
    client_stats.devices = json.dumps(devices)
    client_stats.modules = json.dumps(modules)
    client_stats.save()
