from django import shortcuts
from django.apps import apps
from django.contrib import messages
from django.db import models as django_models
from django.views import generic
from django.utils import decorators
from django.contrib.auth import decorators as auth_decorators
from django.utils.translation import ugettext_lazy as _

from tulius import models as tulius
from tulius.forum import models as forum
from tulius.games import models as games
from tulius.players import models
from tulius.players import forms
from tulius.pm import models as pm
from tulius.stories import models as stories


game_forum = apps.get_app_config('gameforum')

try:
    models.stars.flush_stars_cache()
except:
    pass


def filter_by_games(players):
    return players.filter(
        roles__variation__game__status__in=[
            games.GAME_STATUS_COMPLETED, games.GAME_STATUS_COMPLETED_OPEN
        ]).annotate(
            games=django_models.Count('roles__variation__game', distinct=True))


def filter_by_stories(players):
    return players.annotate(
        stories=django_models.Count('authored_stories')).order_by('-stories')


class PlayersListView(generic.TemplateView):
    template_name = 'players/player_list.haml'

    def get_context_data(self, **kwargs):
        show_games = False
        show_reg_date = False
        show_stories = False
        GET = self.request.GET
        players_filter_form = forms.PlayersFilterForm(GET or None)
        players = tulius.User.objects.filter(is_active=True)
        if GET:
            if GET.get('filter_by_player', None):
                players = players.filter(id=GET['filter_by_player'])
            v = int(GET.get('sort_type', 0))
            if v == forms.PLAYERS_SORT_STORIES_AUTHORED:
                players = filter_by_stories(players)
                show_stories = True
            elif v == forms.PLAYERS_SORT_GAMES_PLAYED_INC:
                players = filter_by_games(players).order_by('games')
                show_games = True
            elif v == forms.PLAYERS_SORT_GAMES_PLAYED_DEC:
                players = filter_by_games(players).order_by('-games')
                show_games = True
            elif v == forms.PLAYERS_SORT_REG_DATE:
                players = players.order_by('date_joined')
                show_reg_date = True
            elif v == forms.PLAYERS_SORT_ALPH:
                players = players.order_by('username')
        else:
            players = filter_by_stories(players)
            show_stories = True
        return {
            'players_filter_form': players_filter_form,
            'players': players,
            'show_games': show_games,
            'show_reg_date': show_reg_date,
            'show_stories': show_stories,
        }


class PlayerView(generic.DetailView):
    queryset = tulius.User.objects.filter(is_active=True)
    pk_url_kwarg = 'player_id'
    context_object_name = 'player'

    def post(self, *args, **kwargs):
        return self.get(*args, **kwargs)


class PlayerDetailsView(PlayerView):
    template_name = 'players/index.haml'

    def get_context_data(self, **kwargs):
        player = self.object
        user = self.request.user
        stats = Statistics(player)
        if stats.total_games > 0:
            played_roles, played_games = get_played(user, player)
            if played_roles.count() > 5:
                played_roles = played_roles[:5]
            if played_games.count() > 5:
                played_games = played_games[:5]
        if user.is_superuser:
            rankform = forms.RankForm(
                data=self.request.POST or None, instance=player)
            if self.request.method == 'POST':
                if rankform.is_valid():
                    rankform.save()
                    messages.success(
                        self.request, _('rank was successfully updated'))
                else:
                    messages.error(
                        self.request,
                        _('there were some errors during form validation'))
        return locals()


class PlayerHistoryView(generic.TemplateView):
    template_name = 'players/player_history.haml'

    @decorators.method_decorator(auth_decorators.login_required)
    def get(self, request, *args, **kwargs):
        return super(PlayerHistoryView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        player = shortcuts.get_object_or_404(
            tulius.User, is_active=True, pk=kwargs['player_id'])
        return {
            'player': player,
            'message_list': pm.PrivateMessage.objects.talking(
                self.request.user, player),
            'message_on_page': 50,
        }


class Statistics:
    def __init__(self, user):
        self.posts = forum.Comment.objects.filter(
            user=user, plugin_id=None).count()
        self.game_posts = forum.Comment.objects.filter(
            user=user, plugin_id=game_forum.GAME_FORUM_SITE_ID).count()
        variation_ids = [
            role['variation'] for role in
            stories.Role.objects.filter(
                user=user).values('variation').distinct()]
        variations = stories.Variation.objects.filter(id__in=variation_ids)
        variations = variations.filter(
            game__status__in=[
                games.GAME_STATUS_COMPLETED, games.GAME_STATUS_COMPLETED_OPEN])
        self.games_won = games.GameWinner.objects.filter(user=user).count()
        self.games_admin = games.GameAdmin.objects.filter(user=user).count()
        self.story_admin = stories.StoryAdmin.objects.filter(user=user).count()
        self.story_author = stories.StoryAuthor.objects.filter(
            user=user).count()
        self.total_games = variations.count()


def get_played(request_user, player=None):
    if player:
        user = player
    else:
        user = request_user
    played_games = []
    played_roles = stories.Role.objects.filter(
        user=user,
        variation__game__status__in=[
            games.GAME_STATUS_COMPLETED, games.GAME_STATUS_COMPLETED_OPEN]
    ).order_by('-variation__game__id')
    for role in played_roles:
        if role.variation.game.read_right(request_user):
            role.variation.game.url = role.variation.thread.get_absolute_url
        played_games = [role.variation.game.id] + played_games
    played_games_uniq = games.Game.objects.filter(
        id__in=played_games).order_by('-id')
    for game in played_games_uniq:
        if game.read_right(request_user):
            game.url = game.variation.thread.get_absolute_url
    return played_roles, played_games_uniq


class LoginTemplateView(generic.TemplateView):
    @decorators.method_decorator(auth_decorators.login_required)
    def get(self, request, *args, **kwargs):
        return super(LoginTemplateView, self).get(request, *args, **kwargs)


class PlayerProfileView(LoginTemplateView):
    template_name = 'profile/index.haml'

    @decorators.method_decorator(auth_decorators.login_required)
    def post(self, *args, **kwargs):
        return self.get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        request = self.request
        stats = Statistics(request.user)
        played_games = []
        played_roles = []
        if stats.total_games > 0:
            played_roles, played_games = get_played(request.user)
            if played_roles.count() > 5:
                played_roles = played_roles[:5]

        rankform = None
        if request.user.is_superuser:
            rankform = forms.RankForm(
                data=request.POST or None, instance=request.user)
            if request.method == 'POST':
                if rankform.is_valid():
                    rankform.save()
                    messages.success(
                        request, _('rank was successfully updated'))
                else:
                    messages.error(
                        request,
                        _('there were some errors during form validation'))
        return {
            'rankform': rankform,
            'played_games': played_games,
            'played_roles': played_roles,
            'stats': stats,
        }


class PlayerPlayedView(LoginTemplateView):
    template_name = 'profile/played.haml'

    def get_context_data(self, **kwargs):
        played_roles, played_games = get_played(self.request.user)
        return {
            'played_roles': played_roles,
            'played_games': played_games,
            'roles_on_page': 50,
        }


class PlayerUserProfileView(PlayerView):
    template_name = 'players/played.haml'

    def get_context_data(self, **kwargs):
        played_roles, played_games = get_played(self.request.user, self.object)
        return {
            'player': self.object,
            'played_roles': played_roles,
            'played_games': played_games,
            'items_on_page': 50,
        }


class PlayerUploadedFilesView(LoginTemplateView):
    template_name = 'profile/files.haml'

    def get_context_data(self, **kwargs):
        return {
            'files': forum.UploadedFile.objects.filter(user=self.request.user)
        }
