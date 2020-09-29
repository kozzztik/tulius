from django.utils.translation import gettext_lazy as _
from django import forms

GRAPH_TYPE_LINEAR = 0
GRAPH_TYPE_LINEAR_C = 1
GRAPH_TYPE_SUNLIGHT = 2

GRAPH_TYPE_CHOICES = (
    (GRAPH_TYPE_LINEAR, 'Linear'),
    (GRAPH_TYPE_LINEAR_C, 'Combined'),
    (GRAPH_TYPE_SUNLIGHT, 'Sunlight'),
)

LINEAR_CALLS = 0
LINEAR_ERRORS = 1
LINEAR_ANONS = 2
LINEAR_MOBILES = 3
LINEAR_EXEC_TIME = 4
LINEAR_DB_CALLS = 5
LINEAR_DB_EXEC = 6
LINEAR_TEMPLATE = 7

LINEAR_GRAPH_CHOICES = (
    (LINEAR_CALLS, 'Calls to site'),
    (LINEAR_ERRORS, 'Exceptions'),
    (LINEAR_ANONS, 'Anonymous calls'),
    (LINEAR_MOBILES, 'Mobile devices'),
    (LINEAR_EXEC_TIME, 'Execution time, s'),
    (LINEAR_DB_CALLS, 'Database queries'),
    (LINEAR_DB_EXEC, 'Database work time, s'),
    (LINEAR_TEMPLATE, 'Template rendering, s'),
)

LINEAR_C_ANONS = 0
LINEAR_C_MOBILES = 1
LINEAR_C_EXEC = 2
LINEAR_C_ERRORS = 3

LINEAR_C_GRAPH_CHOICES = (
    (LINEAR_C_ANONS, 'Anonymous'),
    (LINEAR_C_MOBILES, 'Mobile devices'),
    (LINEAR_C_EXEC, 'Loading view, s'),
    (LINEAR_C_ERRORS, 'Exceptions'),
)

SUNLIGHT_BROWSERS = 0
SUNLIGHT_OSES = 1
SUNLIGHT_MOBILES = 2
SUNLIGHT_MOD_CALLS = 3
SUNLIGHT_MOD_ANONS = 4
SUNLIGHT_MOD_MOBILES = 5
SUNLIGHT_MOD_EXCEPT = 7
SUNLIGHT_MOD_EXEC = 6
SUNLIGHT_MOD_DB_COUNT = 8
SUNLIGHT_MOD_DB_TIME = 9
SUNLIGHT_MOD_TEMPLATE = 10

SUNLIGHT_CHOICES = (
    (SUNLIGHT_BROWSERS, 'Browsers'),
    (SUNLIGHT_OSES, 'OSes'),
    (SUNLIGHT_MOBILES, 'Mobile devices'),
    (SUNLIGHT_MOD_CALLS, 'Modules - Calls'),
    (SUNLIGHT_MOD_ANONS, 'Modules - Anonymous'),
    (SUNLIGHT_MOD_MOBILES, 'Modules - Mobiles'),
    (SUNLIGHT_MOD_EXCEPT, 'Modules - Exceptions'),
    (SUNLIGHT_MOD_EXEC, 'Modules - Execution time'),
    (SUNLIGHT_MOD_DB_COUNT, 'Modules - DB queries'),
    (SUNLIGHT_MOD_DB_TIME, 'Modules - DB work time'),
    (SUNLIGHT_MOD_TEMPLATE, 'Modules - Rendering'),
)

PERIOD_DAY = 1
PERIOD_LASTDAY = 2
PERIOD_3DAYS = 3
PERIOD_WEEK = 7
PERIOD_2WEEKS = 12
PERIOD_3WEEKS = 21
PERIOD_MONTH = 30

PERIOD_CHOICES = (
    (PERIOD_DAY, 'Today'),
    (PERIOD_LASTDAY, 'Yesterday'),
    (PERIOD_3DAYS, 'Last 3 days'),
    (PERIOD_WEEK, 'This week'),
    (PERIOD_2WEEKS, 'Last 2 weeks'),
    (PERIOD_3WEEKS, 'Last 3 weeks'),
    (PERIOD_MONTH, 'Last month'),
)


class StatsFilterForm(forms.Form):
    graph_type = forms.ChoiceField(
        required=True,
        choices=GRAPH_TYPE_CHOICES,
        label=_(u'type'),
    )
    linear_type = forms.ChoiceField(
        required=True,
        choices=LINEAR_GRAPH_CHOICES,
        label=_(u'report'),
    )
    linear_c_type = forms.ChoiceField(
        required=True,
        choices=LINEAR_C_GRAPH_CHOICES,
        label=_(u'report'),
    )
    sunlight_type = forms.ChoiceField(
        required=True,
        choices=SUNLIGHT_CHOICES,
        label=_(u'report'),
    )
    period = forms.ChoiceField(
        required=True,
        choices=PERIOD_CHOICES,
        label=_(u'report'),
    )
