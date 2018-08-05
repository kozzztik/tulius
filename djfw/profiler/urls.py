from django.conf import urls

from djfw.profiler import views
from djfw.profiler import time_selector

app_name = 'djfw.profiler'

urlpatterns = [
    urls.url(
        r'^reports/auditory/$',
        views.AuditoryReport.as_view(),
        name='auditory_report'),
    urls.url(
        r'^reports/loading/$',
        views.LoadingReport.as_view(),
        name='loading_report'),
    urls.url(
        r'^reports/browsers/$',
        views.BrowsersReport.as_view(),
        name='browsers_report'),
    urls.url(
        r'^reports/oses/$',
        views.OsesReport.as_view(),
        name='oses_report'),
    urls.url(
        r'^reports/modules/$',
        views.ModulesReport.as_view(),
        name='modules_report'),
    urls.url(
        r'^reports/mobiles/$',
        views.MobilesReport.as_view(),
        name='mobiles_report'),
    urls.url(
        r'^reports/devices/$',
        views.DevicesReport.as_view(),
        name='devices_report'),
    urls.url(
        r'^reports/distribution/$',
        views.DistributionReport.as_view(),
        name='distribution_report'),
    urls.url(
        r'^set_time_selector/$',
        time_selector.SetTimePeriod.as_view(),
        name='set_time_selector'),
]
