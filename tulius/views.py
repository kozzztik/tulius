import datetime

from django import http
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.template import response
from django.views import generic
from django.utils import timezone

from djfw.news import models as news
from djfw.profiler import graphs
from djfw.flatpages import models as flatpage_models

from tulius import forms
from tulius.profile import views as profile_views
from tulius.games import models as games
from tulius.websockets import context_processors as websock_context


class HomeView(generic.TemplateView):
    template_name = 'home.haml'

    def get_context_data(self, **kwargs):
        user = self.request.user
        return {
            'announced_games': games.Game.objects.new_games(user),
            'request_accepting_games': games.Game.objects.announced_games(
                user),
            'awaiting_start_games': games.Game.objects.awaiting_start_games(
                user),
            'current_games': games.Game.objects.current_games(user),
            'news': news.NewsItem.objects.filter(
                is_published=True
            ).filter(
                published_at__lt=timezone.now()).order_by('-published_at')[:3],
        }


def error404(request, template_name='404.html', **kwargs):
    return response.TemplateResponse(request, template_name, status=404)


def error500(request, template_name='500.haml'):
    return response.TemplateResponse(request, template_name, status=500)


class ArticlesAPI(generic.View):
    def get(self, *args, **kwargs):
        pages = flatpage_models.FlatPage.objects.filter(
            is_enabled=True, show_on_home=True)
        return http.JsonResponse({'pages': [{
            'title': page.title,
            'url': page.url,
        } for page in pages]})


class AppSettingsAPI(generic.View):
    def get(self, request, **kwargs):
        return http.JsonResponse({
            'debug': settings.DEBUG,
            'websockets_url': websock_context.default(
                request, True)['WEBSOCKET_URI'],
            'user': profile_views.request_user_json(request),
        })


def logic_time(x):
    time = x.template_time + x.db_time
    if time > x.exec_time:
        return time
    return x.exec_time - time


class StatisticsView(generic.TemplateView):
    template_name = 'statistics.haml'

    # pylint: disable=too-many-branches,too-many-statements
    def get_context_data(self, **kwargs):
        form = forms.StatsFilterForm(self.request.GET or None)
        graph_type = forms.GRAPH_TYPE_LINEAR
        linear_type = forms.LINEAR_CALLS
        linear_c_type = forms.LINEAR_C_ANONS
        sunlight_type = forms.SUNLIGHT_BROWSERS
        days = 1
        day = datetime.date.today()
        day_start = datetime.datetime(
            day.year, day.month, day.day,
            tzinfo=timezone.get_current_timezone())

        graph = None

        if self.request.GET:
            if ('graph_type' in self.request.GET) and \
                    self.request.GET['graph_type']:
                graph_type = int(self.request.GET['graph_type'])
            if ('linear_type' in self.request.GET) and \
                    self.request.GET['linear_type']:
                linear_type = int(self.request.GET['linear_type'])
            if ('linear_c_type' in self.request.GET) and \
                    self.request.GET['linear_c_type']:
                linear_c_type = int(self.request.GET['linear_c_type'])
            if ('sunlight_type' in self.request.GET) and \
                    self.request.GET['sunlight_type']:
                sunlight_type = int(self.request.GET['sunlight_type'])
            if ('period' in self.request.GET) and self.request.GET['period']:
                days = int(self.request.GET['period'])

        day_start = day_start - datetime.timedelta(days=days)
        if graph_type == forms.GRAPH_TYPE_LINEAR:
            if linear_type == forms.LINEAR_CALLS:
                graph = graphs.collapsed_time_period_graph(
                    day_start, days, 'calls_count')
            elif linear_type == forms.LINEAR_ERRORS:
                graph = graphs.collapsed_time_period_graph(
                    day_start, days, 'exceptions_count')
            elif linear_type == forms.LINEAR_ANONS:
                graph = graphs.collapsed_time_period_graph(
                    day_start, days, 'anon_calls_count')
            elif linear_type == forms.LINEAR_MOBILES:
                graph = graphs.collapsed_time_period_graph(
                    day_start, days, 'mobiles_count')
            elif linear_type == forms.LINEAR_EXEC_TIME:
                graph = graphs.collapsed_time_period_graph(
                    day_start, days, 'exec_time', multi=0.001)
            elif linear_type == forms.LINEAR_DB_CALLS:
                graph = graphs.collapsed_time_period_graph(
                    day_start, days, 'db_count')
            elif linear_type == forms.LINEAR_DB_EXEC:
                graph = graphs.collapsed_time_period_graph(
                    day_start, days, 'db_time', multi=0.001)
            elif linear_type == forms.LINEAR_TEMPLATE:
                graph = graphs.collapsed_time_period_graph(
                    day_start, days, 'template_time', multi=0.001)
        elif graph_type == forms.GRAPH_TYPE_SUNLIGHT:
            if sunlight_type == forms.SUNLIGHT_BROWSERS:
                graph = graphs.collapsed_sunlignt_graph(
                    day_start, days, 'browsers')
                graph['name'] = _("Browsers")
            elif sunlight_type == forms.SUNLIGHT_OSES:
                graph = graphs.collapsed_sunlignt_graph(
                    day_start, days, 'oses')
                graph['name'] = _("Operating systems")
            elif sunlight_type == forms.SUNLIGHT_MOBILES:
                graph = graphs.collapsed_sunlignt_graph(
                    day_start, days, 'devices')
                graph['name'] = _("Mobile devices")
            elif sunlight_type == forms.SUNLIGHT_MOD_CALLS:
                graph = graphs.collapsed_sunlignt_graph(
                    day_start, days, 'modules', subfield="calls")
                graph['name'] = _("Calls")
            elif sunlight_type == forms.SUNLIGHT_MOD_ANONS:
                graph = graphs.collapsed_sunlignt_graph(
                    day_start, days, 'modules', subfield="anons")
                graph['name'] = _("Anonymous")
            elif sunlight_type == forms.SUNLIGHT_MOD_MOBILES:
                graph = graphs.collapsed_sunlignt_graph(
                    day_start, days, 'modules', subfield="mobiles")
                graph['name'] = _("Mobiles")
            elif sunlight_type == forms.SUNLIGHT_MOD_EXCEPT:
                graph = graphs.collapsed_sunlignt_graph(
                    day_start, days, 'modules', subfield="exceptions")
                graph['name'] = _("Exceptions")
            elif sunlight_type == forms.SUNLIGHT_MOD_EXEC:
                graph = graphs.collapsed_sunlignt_graph(
                    day_start, days, 'modules', subfield="exec")
                graph['name'] = _("Exec time")
            elif sunlight_type == forms.SUNLIGHT_MOD_DB_COUNT:
                graph = graphs.collapsed_sunlignt_graph(
                    day_start, days, 'modules', subfield="db_count")
                graph['name'] = _("DB queries")
            elif sunlight_type == forms.SUNLIGHT_MOD_DB_TIME:
                graph = graphs.collapsed_sunlignt_graph(
                    day_start, days, 'modules', subfield="db_time")
                graph['name'] = _("DB time")
            elif sunlight_type == forms.SUNLIGHT_MOD_TEMPLATE:
                graph = graphs.collapsed_sunlignt_graph(
                    day_start, days, 'modules', subfield="render")
                graph['name'] = _("Template rendering")
        elif graph_type == forms.GRAPH_TYPE_LINEAR_C:
            if linear_c_type == forms.LINEAR_C_ANONS:
                graph = graphs.collapsed_sum_graph(
                    day_start, days,
                    ['calls_count', 'anon_calls_count'],
                    [_("All"), _("Anonymous")])
            elif linear_c_type == forms.LINEAR_C_MOBILES:
                graph = graphs.collapsed_sum_graph(
                    day_start, days,
                    ['calls_count', 'mobiles_count'],
                    [_("All"), _("Mobile devices")])
            elif linear_c_type == forms.LINEAR_C_EXEC:
                graph = graphs.collapsed_sum_graph(
                    day_start, days,
                    [logic_time, 'db_time', 'template_time'],
                    [_("Logic"), _("DB"), _("Rendering")],
                    multi=0.001, incremental=True)
            elif linear_c_type == forms.LINEAR_C_ERRORS:
                graph = graphs.collapsed_sum_graph(
                    day_start, days,
                    ['calls_count', 'exceptions_count'],
                    [_("All"), _("Exceptions")])
        kwargs['form'] = form
        kwargs['graph_type'] = graph_type
        kwargs['graph'] = graph
        return kwargs
