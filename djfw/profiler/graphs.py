import datetime
import json

from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import make_naive, utc
from django.conf import settings
from django.db.models import Count, Sum, Avg, Min, Max

from djfw.profiler.models import ClientCollapse
from .models import ProfilerMessage, TimeCollapse
from .collapse import COLLAPSE_INTERVALS


def time_period_graph(request, *args, **kwargs):
    endtime = request.profiler_period.end
    starttime = request.profiler_period.start
    intervals = request.profiler_period.intervals
    weight_field = request.profiler_period.weight_field

    def annotate_stats(query):
        if weight_field:
            return query.annotate(
                weight_count=Count(weight_field),
                weight_sum=Sum(weight_field), weight_avg=Avg(weight_field))
        return query.annotate(weight_sum=Count('id'))

    delta = (endtime - starttime) / intervals
    data = []
    period_query = ProfilerMessage.objects.filter(
        create_time__lte=endtime, create_time__gte=starttime)
    modules = period_query.order_by(
        'module_name').distinct().values('module_name')
    modules = annotate_stats(modules).order_by('-weight_sum')
    all_modules_sum = 0
    all_modules_count = 0
    all_modules_avg = 0
    module_list = []
    for module in modules:
        functions = period_query.filter(
            module_name=module['module_name']).order_by('func_name').distinct()
        functions = annotate_stats(functions.values('func_name'))
        module_data = {'module_name': module['module_name']}
        module_data['functions'] = functions
        module_data['sum'] = module['weight_sum']
        all_modules_sum += module['weight_sum']
        if weight_field:
            module_data['count'] = module['weight_count']
            all_modules_count += module['weight_count']
            module_data['avg'] = module['weight_avg']
            all_modules_avg += module['weight_avg']
        module_list += [module_data]
    for i in range(intervals):
        interval_start = starttime + (delta * i)
        interval_end = starttime + (delta * (i + 1))
        subquery = {'create_time__gte': interval_start}
        if i == intervals - 1:
            subquery['create_time__lte'] = interval_end
        else:
            subquery['create_time__lt'] = interval_end
        period_query = ProfilerMessage.objects.filter(**subquery)
        values = period_query.order_by(
            'module_name').distinct().values('module_name')
        if weight_field:
            values = values.annotate(weight_sum=Sum(weight_field))
        else:
            values = values.annotate(weight_sum=Count('id'))
        period_data = []
        for module in module_list:
            module_values = [0]
            for j in values:
                if module['module_name'] == j['module_name']:
                    module_values = [j['weight_sum']]
                    break
            period_data += module_values

        if settings.USE_TZ:
            data += [[make_naive(interval_end, utc), period_data]]
        else:
            data += [[interval_end, period_data]]
    graph = {
        'data': data,
        'modules': module_list,
        'details': weight_field,
        'modules_sum': all_modules_sum,
        'modules_count': all_modules_count,
        'modules_avg': all_modules_avg}
    return graph


def time_period_graph_sum(request, *args, **kwargs):
    endtime = request.profiler_period.end
    starttime = request.profiler_period.start
    intervals = request.profiler_period.intervals
    weight_field = request.profiler_period.weight_field

    delta = (endtime - starttime) / intervals
    data = []
    for i in range(intervals):
        interval_start = starttime + (delta * i)
        interval_end = starttime + (delta * (i + 1))
        subquery = {'create_time__gte': interval_start}
        if i == intervals - 1:
            subquery['create_time__lte'] = interval_end
        else:
            subquery['create_time__lt'] = interval_end
        period_query = ProfilerMessage.objects.filter(**subquery)
        if weight_field:
            values = period_query.aggregate(weight_sum=Sum(weight_field))
        else:
            values = period_query.aggregate(weight_sum=Count('id'))
        value = values['weight_sum']
        if settings.USE_TZ:
            data += [[make_naive(interval_end, utc), value if value else 0]]
        else:
            data += [[interval_end, value if value else 0]]
    return data


def sunlignt_graph(request, category_field, category_subfield=None):
    endtime = request.profiler_period.end
    starttime = request.profiler_period.start
    weight_field = request.profiler_period.weight_field
    period_query = ProfilerMessage.objects.filter(
        create_time__lte=endtime, create_time__gte=starttime)
    all_weight = 0
    categories = period_query.order_by(
        category_field).distinct().values(category_field)
    if weight_field:
        categories = categories.annotate(weight=Sum(weight_field))
    else:
        categories = categories.annotate(weight=Count(category_field))
    # spider devices hack
    if category_field == 'device':
        categories = categories.exclude(device="Spider")
    categories = categories.order_by('-weight')
    data = []
    for category_obj in categories:
        all_weight += category_obj['weight']
    for category_obj in categories:
        category = {}
        category_weight = category_obj['weight']
        if not category_weight:
            continue
        category_id = category_obj[category_field]
        category['weight'] = int(category_weight)
        category['percentage'] = int(category_weight * 100.0 / all_weight)
        category['label'] = category_id
        category['id'] = category_id
        category['sublabel'] = (
            "%s %s (%.1f%%)" % (
                str(_("Views:")), category_weight, category['percentage']))
        if category_subfield:
            category_elems = []
            subquery = {}
            subquery[category_field] = category_id
            elems = period_query.filter(**subquery).order_by(
                category_subfield).distinct().values(category_subfield)
            if weight_field:
                elems = elems.annotate(weight=Sum(weight_field))
            else:
                elems = elems.annotate(weight=Count(category_subfield))
            elems = elems.order_by('-weight')
            for elem in elems:
                category_elem = {}
                category_elem_weight = elem['weight']
                if len(elems) == 1:
                    category_elem_weight = category_weight
                category_elem['weight'] = int(category_elem_weight)
                category_elem['percentage'] = \
                    category_elem_weight * 100.0 / category_weight
                category_elem['percentage_total'] = \
                    category_elem_weight * 100.0 / all_weight
                category_elem['id'] = \
                    "%s %s" % (category_id, elem[category_subfield])
                category_elem['name'] = elem[category_subfield] or "-"
                category_elem['label'] = \
                    category_id + " " + (elem[category_subfield] or "")
                category_elem['sublabel'] = str(_("Views:")) +\
                    "%s (%s: %.1f%%, " % (
                        category_elem_weight, category_id,
                        category_elem['percentage'],) +\
                    str(_("All:")) + " %.1f%%)" % (
                        category_elem['percentage_total'],)
                category_elems += [category_elem]
            category['data'] = category_elems
        data += [category]
    return {
        'weight': all_weight,
        'data': data,
        'category_name': category_field,
        'id': category_field,
        'weight_name': request.profiler_period.weight_title,
        'category_subfield': category_subfield}


def distribution_graph(
        request, module_name=None, function_name=None, intervals=20):
    endtime = request.profiler_period.end
    starttime = request.profiler_period.start
    weight_field = request.profiler_period.weight_field
    if not weight_field:
        return None
    delta = (endtime - starttime) / intervals
    data = []
    period_query = ProfilerMessage.objects.filter(
        create_time__lte=endtime, create_time__gte=starttime)
    values = period_query.aggregate(
        weight_min=Min(weight_field), weight_max=Max(weight_field))
    value_max = values['weight_max']
    value_min = values['weight_min']
    delta = (value_max - value_min + 0.0) / intervals
    data = []
    for i in range(intervals):
        interval_start = value_min + (delta * i)
        interval_end = value_min + (delta * (i + 1))
        subquery = {weight_field + '__gte': interval_start}
        if i == intervals - 1:
            subquery[weight_field + '__lte'] = interval_end
        else:
            subquery[weight_field + '__lt'] = interval_end
        value = ProfilerMessage.objects.filter(**subquery).count()
        x = (interval_end + interval_start) / 2
        data += [[x, value, interval_start, interval_end]]
    return data


PARTING_DAYS = 6


def collapsed_time_period_graph(start_day, days, weight_field, multi=1):
    intervals = days if days > PARTING_DAYS else COLLAPSE_INTERVALS * days
    delta = datetime.timedelta(days=1)
    if days <= PARTING_DAYS:
        delta = delta / COLLAPSE_INTERVALS
    data = []

    for i in range(intervals):
        interval_start = start_day + (delta * i)
        interval_end = start_day + (delta * (i + 1))
        query = TimeCollapse.objects.filter(day=interval_start)
        if days <= PARTING_DAYS:
            query = query.filter(
                create_time__gte=interval_start, create_time__lt=interval_end)
        query = query.aggregate(weight_sum=Sum(weight_field))
        value = query['weight_sum']
        value = int(value * multi) if value else 0
        data += [[interval_end, value]]
    return data


def collapsed_sunlignt_graph(
        start_day, days, weight_field, subfield=None, mappings=None,
        strict_mappings=False):
    category_subfield = weight_field != 'devices'
    categories = {}
    for i in range(days):
        try:
            day_data = ClientCollapse.objects.get(
                day=start_day + datetime.timedelta(days=i))
        except:
            day_data = None
        if day_data:
            value_str = getattr(day_data, weight_field)
            value_dict = json.loads(value_str)
            for category in value_dict.keys():
                if category == 'Spider':
                    continue
                if category not in categories:
                    if category_subfield:
                        categories[category] = {}
                    else:
                        categories[category] = 0
                if category_subfield:
                    for subcategory in value_dict[category].keys():
                        if subfield:
                            value = value_dict[category][subcategory][subfield]
                        else:
                            value = value_dict[category][subcategory]
                        if subcategory not in categories[category]:
                            categories[category][subcategory] = value
                        else:
                            categories[category][subcategory] += value
                else:
                    categories[category] += value_dict[category]
    data = []
    all_weight = 0
    for category in categories:
        c = {'id': category, 'label': category}
        if mappings:
            if category in mappings:
                c['label'] = mappings[category]['label']
            elif strict_mappings:
                continue
        weight = 0
        if category_subfield:
            subdata = []
            for subcategory in categories[category].keys():
                subweight = categories[category][subcategory]
                elem = {'name': subcategory or "-", 'weight': subweight}
                elem['id'] = "%s %s" % (category, subcategory)
                if subfield:
                    elem['label'] = subcategory
                else:
                    elem['label'] = category + " " + (subcategory or "")
                if mappings and category in mappings:
                    if subcategory in mappings[category]['items']:
                        elem['label'] = mappings[category]['items'][
                            subcategory]
                    elif strict_mappings:
                        continue
                subdata += [elem]
                weight += subweight
            c['data'] = sorted(
                subdata, key=lambda x: x['weight'], reverse=True)
        else:
            weight = categories[category]
        c['weight'] = weight
        all_weight += weight
        if weight > 0:
            data += [c]
    for category in data:
        category_weight = category['weight']
        category['percentage'] = int(category_weight * 100.0 / all_weight)
        category['sublabel'] = (
            "%s %s (%.1f%%)" % (
                str(_("Views:")), category_weight, category['percentage']))
        if category_subfield:
            for subcategory in category['data']:
                sub_weight = subcategory['weight']
                subcategory['percentage'] = \
                    sub_weight * 100.0 / category_weight
                subcategory['percentage_total'] = \
                    sub_weight * 100.0 / all_weight
                subcategory['sublabel'] = str(_("Views:")) +\
                    "%s (%s: %.1f%%, " % (
                        sub_weight, category['label'],
                        subcategory['percentage'],) +\
                    str(_("All:")) + " %.1f%%)" % (subcategory[
                        'percentage_total'],)
    data = sorted(data, key=lambda x: x['weight'], reverse=True)
    return {
        'weight': all_weight,
        'data': data,
        'category_name': weight_field,
        'id': weight_field,
        'category_subfield': category_subfield}


def collapsed_sum_graph(
        start_day, days, weight_fields, captions, incremental=False, multi=1):
    intervals = days if days > PARTING_DAYS else COLLAPSE_INTERVALS * days
    delta = datetime.timedelta(days=1)
    if days <= PARTING_DAYS:
        delta = delta / COLLAPSE_INTERVALS
    data = []

    for i in range(intervals):
        interval_start = start_day + (delta * i)
        interval_end = start_day + (delta * (i + 1))
        query = TimeCollapse.objects.filter(day=interval_start)
        if days <= PARTING_DAYS:
            query = query.filter(
                create_time__gte=interval_start, create_time__lt=interval_end)
        value = [0 for w in weight_fields]
        for q in query:
            for x, weight_field in enumerate(weight_fields):
                if callable(weight_field):
                    v = weight_field(q)
                else:
                    v = getattr(q, weight_field)
                v = int(v * multi) if v else 0
                value[x] += v
        data += [[interval_end, value if value else 0]]
    return {"data": data, "captions": captions, 'incremental': incremental}
