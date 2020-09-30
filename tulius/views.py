import datetime

from django import http
from django.conf import settings
from django.core import exceptions
from django.template import response
from django.views import generic
from django.utils import timezone

from djfw.news import models as news
from djfw.flatpages import models as flatpage_models

from tulius.profile import views as profile_views
from tulius.games import models as games
from tulius.websockets import context_processors as websock_context
from tulius import celery


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


class IndexVue(generic.TemplateView):
    template_name = 'base_vue.html'


class CeleryStatusAPI(generic.View):
    @staticmethod
    def get(request, **_kwargs):
        if not request.user.is_superuser:
            raise exceptions.PermissionDenied()
        active = celery.app.control.inspect().active() or {}
        for worker_data in active.values():
            for task in worker_data:
                task['time_start'] = str(
                    datetime.datetime.fromtimestamp(task['time_start']))
        return http.JsonResponse({
            'stats': celery.app.control.inspect().stats() or {},
            'active': active,
        })
