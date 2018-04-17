import datetime

from django import urls
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now

from .forms import TimeSelectorForm


TIME_SELECTOR_LAST_DAY = 0
TIME_SELECTOR_LAST_WEEK = 1
TIME_SELECTOR_LAST_MONTH = 2
TIME_SELECTOR_TODAY = 3
TIME_SELECTOR_THISWEEK = 4
TIME_SELECTOR_THISMONTH = 5
TIME_SELECTOR_PRDAY = 6
TIME_SELECTOR_PRWEEK = 7
TIME_SELECTOR_PRMONTH = 8

WEIGHT_SELECTOR_CALLS = 0
WEIGHT_SELECTOR_EXEC_TIME = 1
WEIGHT_SELECTOR_DB_TIME = 2
WEIGHT_SELECTOR_DB_COUNT = 3
WEIGHT_SELECTOR_TEMPLATE_TIME = 4
WEIGHT_SELECTOR_TEMPLATE_DB_TIME = 5
WEIGHT_SELECTOR_TEMPLATE_DB_COUNT = 6
WEIGHT_SELECTOR_EXCEPTIONS = 7


class LastTime(object):
    def __init__(
            self, offset_days=0, offset_month=0, round_day=False,
            round_month=False, round_week=False):
        self.offset_days = offset_days
        self.offset_month = offset_month
        self.round_day = round_day 
        self.round_month = round_month
        self.round_week = round_week
        
    def month_offset(self, value, offset):
        target_month = value.year * 12 + value.month + offset
        target_year = (target_month - 1) // 12
        target_month = ((target_month - 1 - (target_year * 12)) % 12) + 1
        return value.replace(year=target_year, month=target_month)

    def __call__(self, *args, **kwargs):
        value = now()
        if self.round_day or self.round_week or self.round_month:
            value = value.replace(hour=0, minute=0, second=0, microsecond=0)
            if self.round_day:
                value += datetime.timedelta(days=1)
        if self.round_month:
            value = value.replace(day=1)
            value = self.month_offset(value, 1)
        if self.round_week:
            value -= datetime.timedelta(days=value.weekday())
            value += datetime.timedelta(days=7)
        value -= datetime.timedelta(days=self.offset_days)
        if self.offset_month:
            value = self.month_offset(value, -self.offset_month)
        return value


class TimePeriod(object):
    start = 0
    end = 0
    intervals = 0
    num = 0
    weight_num = 0
    weight_field = None
    weight_title = ""


WEIGHT_SELECTION = (
    (WEIGHT_SELECTOR_CALLS, _(u'Calls'), None, _('Count')),
    (WEIGHT_SELECTOR_EXEC_TIME,  _(u'Execution time'), 'exec_time', _('Time')),
    (WEIGHT_SELECTOR_DB_TIME,  _(u'DB work time'), 'db_time', _('Time')),
    (WEIGHT_SELECTOR_DB_COUNT,
     _(u'DB queries count'), 'db_count', _('Count')),
    (WEIGHT_SELECTOR_TEMPLATE_TIME,
     _(u'Template rendering time'), 'template_time', _('Time')),
    (WEIGHT_SELECTOR_TEMPLATE_DB_TIME,
     _(u'Template DB work time'), 'template_db_time', _('Time')),
    (WEIGHT_SELECTOR_TEMPLATE_DB_COUNT,
     _(u'Template DB queries count'), 'template_db_count', _('Count')),
    (WEIGHT_SELECTOR_EXCEPTIONS,  _(u'Exceptions count'), 'error', _('Count')),
)

TIME_SELECTION = (
    (TIME_SELECTOR_LAST_DAY, _(u'last day'), LastTime(1), LastTime(), 96),
    (TIME_SELECTOR_LAST_WEEK, _(u'last week'), LastTime(7), LastTime(), 84),
    (TIME_SELECTOR_LAST_MONTH, _(u'last month'), LastTime(0, 1),
     LastTime(), 64),
    (TIME_SELECTOR_TODAY, _(u'today'), LastTime(1, round_day=True),
     LastTime(round_day=True), 96),
    (TIME_SELECTOR_THISWEEK, _(u'this week'), LastTime(7, round_week=True),
     LastTime(round_week=True), 84),
    (TIME_SELECTOR_THISMONTH, _(u'this month'),
     LastTime(0, 1, round_month=True), LastTime(round_month=True), 64),
    (TIME_SELECTOR_PRDAY, _(u'previous day'),
     LastTime(2, round_day=True), LastTime(1, round_day=True), 96),
    (TIME_SELECTOR_PRWEEK, _(u'previous week'),
     LastTime(14, round_week=True), LastTime(7, round_week=True), 84),
    (TIME_SELECTOR_PRMONTH, _(u'previous month'),
     LastTime(0, 2, round_month=True), LastTime(0, 1, round_month=True), 64),
)

PROFILER_TIME_SELECTOR = 'profiler_time_selector'
PROFILER_WEIGHT_SELECTOR = 'profiler_weight_selector'


class TimePeriodView(TemplateView):
    def update_request(self, request):
        period = TIME_SELECTION[0]
        weight = WEIGHT_SELECTION[0]
        if PROFILER_TIME_SELECTOR in request.session:
            period = TIME_SELECTION[request.session[PROFILER_TIME_SELECTOR]]
        if PROFILER_WEIGHT_SELECTOR in request.session:
            weight = WEIGHT_SELECTION[
                request.session[PROFILER_WEIGHT_SELECTOR]]
        period_obj = TimePeriod()
        period_obj.num = period[0]
        period_obj.start = period[2]
        period_obj.weight_num = weight[0]
        period_obj.weight_field = weight[2]
        period_obj.weight_title = weight[3]
        if callable(period_obj.start):
            period_obj.start = period_obj.start()
        period_obj.end = period[3]
        if callable(period_obj.end):
            period_obj.end = period_obj.end()
        period_obj.intervals = period[4]
        request.profiler_period = period_obj
        
    def get(self, request, *args, **kwargs):
        self.update_request(request)
        return super(TimePeriodView, self).get(request, *args, **kwargs)


class SetTimePeriod(TimePeriodView):
    template_name = 'profiler/time_selector.html'
    
    def get_context_data(self, **kwargs):
        period_choices = [(period[0], period[1]) for period in TIME_SELECTION]
        weight_choices = [
            (weight[0], weight[1]) for weight in WEIGHT_SELECTION]
        self.form = TimeSelectorForm(
            period_choices, weight_choices, data=self.request.POST or None,
            initial={
                'period': self.request.profiler_period.num,
                'weight': self.request.profiler_period.weight_num})
        return {'form': self.form}
    
    def post(self, request, *args, **kwargs):
        self.update_request(request)
        self.get_context_data(**kwargs)
        if self.form.is_valid():
            period = int(self.form.cleaned_data['period'])
            weight = int(self.form.cleaned_data['weight'])
            request.session[PROFILER_TIME_SELECTOR] = period
            request.session[PROFILER_WEIGHT_SELECTOR] = weight
        return HttpResponseRedirect(
            urls.reverse('admin:profiler_profilermessage_changelist'))
