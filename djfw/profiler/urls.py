from django.conf.urls import url
from .views import *
from .time_selector import SetTimePeriod

app_name = 'djfw.profiler'

urlpatterns = [
    url(
        r'^reports/auditory/$',
        AuditoryReport.as_view(),
        name='auditory_report'),
    url(
        r'^reports/loading/$',
        LoadingReport.as_view(),
        name='loading_report'),
    url(
        r'^reports/browsers/$',
        BrowsersReport.as_view(),
        name='browsers_report'),
    url(
        r'^reports/oses/$',
        OsesReport.as_view(),
        name='oses_report'),
    url(
        r'^reports/modules/$',
        ModulesReport.as_view(),
        name='modules_report'),
    url(
        r'^reports/mobiles/$',
        MobilesReport.as_view(),
        name='mobiles_report'),
    url(
        r'^reports/devices/$',
        DevicesReport.as_view(),
        name='devices_report'),
    url(
        r'^reports/distribution/$',
        DistributionReport.as_view(),
        name='distribution_report'),
    url(
        r'^set_time_selector/$',
        SetTimePeriod.as_view(),
        name='set_time_selector'),
]
