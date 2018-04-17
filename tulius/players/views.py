from django import urls
from django.apps import apps
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView, DetailView
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.db.models import Count
from django.utils.decorators import method_decorator

from tulius.forum.models import UploadedFile, Comment
from tulius.stories.models import StoryAdmin, Role, Variation, StoryAuthor
from tulius.games.models import Game, GAME_STATUS_COMPLETED, \
    GAME_STATUS_COMPLETED_OPEN, GameWinner, GameAdmin
from tulius.games.models import GameGuest
from tulius.models import User
from .models import stars
from .forms import PlayersFilterForm, PLAYERS_SORT_STORIES_AUTHORED,\
    PLAYERS_SORT_GAMES_PLAYED_INC, PLAYERS_SORT_GAMES_PLAYED_DEC, \
    PLAYERS_SORT_REG_DATE, PLAYERS_SORT_ALPH, RankForm
from pm.models import PrivateMessage


game_forum = apps.get_app_config('gameforum')

try:
    stars.flush_stars_cache()
except:
    pass


def filter_by_games(players):
    return players.filter(
        roles__variation__game__status__in=[
            GAME_STATUS_COMPLETED, GAME_STATUS_COMPLETED_OPEN]).annotate(
        games=Count('roles__variation__game', distinct=True))


def filter_by_stories(players):
    return players.annotate(
        stories=Count('authored_stories')).order_by('-stories')


class PlayersListView(TemplateView):
    template_name = 'players/player_list.haml'
    
    def get_context_data(self, **kwargs):
        GET = self.request.GET
        players_filter_form = PlayersFilterForm(GET or None)
        players = User.objects.filter(is_active=True)
        if GET:
            if GET.get('filter_by_player', None):
                players = players.filter(id=GET['filter_by_player'])
            v = int(GET.get('sort_type', 0))
            if v:
                if v == PLAYERS_SORT_STORIES_AUTHORED:
                    players = filter_by_stories(players)
                    show_stories = True
                elif v == PLAYERS_SORT_GAMES_PLAYED_INC:
                    players = filter_by_games(players).order_by('games')
                    show_games = True
                elif v == PLAYERS_SORT_GAMES_PLAYED_DEC:
                    players = filter_by_games(players).order_by('-games')
                    show_games = True
                elif v == PLAYERS_SORT_REG_DATE:
                    players = players.order_by('date_joined')
                    show_reg_date = True
                elif v == PLAYERS_SORT_ALPH:
                    players = players.order_by('username')
        else:
            players = filter_by_stories(players)
            show_stories = True
        return locals()


class PlayerView(DetailView):
    queryset = User.objects.filter(is_active=True)
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
            rankform = RankForm(
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


class PlayerHistoryView(TemplateView):
    template_name = 'players/player_history.haml'
    
    @method_decorator(login_required)
    def get(self, *args, **kwargs):
        return super(PlayerHistoryView, self).get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        player = get_object_or_404(
            User, is_active=True, pk=kwargs['player_id'])
        message_list = PrivateMessage.objects.talking(
            self.request.user, player)
        message_on_page = 50
        return locals()


class Statistics:
    def __init__(self, user):
        self.posts = Comment.objects.filter(user=user, plugin_id=None).count()
        self.game_posts = Comment.objects.filter(
            user=user, plugin_id=game_forum.GAME_FORUM_SITE_ID).count()
        variation_ids = [
            role['variation'] for role in
            Role.objects.filter(user=user).values('variation').distinct()]
        variations = Variation.objects.filter(id__in=variation_ids)
        variations = variations.filter(
            game__status__in=[
                GAME_STATUS_COMPLETED, GAME_STATUS_COMPLETED_OPEN])
        self.games_won = GameWinner.objects.filter(user=user).count()
        self.games_admin = GameAdmin.objects.filter(user=user).count()
        self.story_admin = StoryAdmin.objects.filter(user=user).count()
        self.story_author = StoryAuthor.objects.filter(user=user).count()
        self.total_games = variations.count()   


def get_played(request_user, player=None):
    if player:
        user = player
    else:
        user = request_user
    played_games = []    
    played_roles = Role.objects.filter(
        user=user,
        variation__game__status__in=[
            GAME_STATUS_COMPLETED, GAME_STATUS_COMPLETED_OPEN]
    ).order_by('-variation__game__id')
    for role in played_roles:
        if role.variation.game.read_right(request_user):
            role.variation.game.url = role.variation.thread.get_absolute_url
        played_games = [role.variation.game.id] + played_games
    played_games_uniq = Game.objects.filter(
        id__in=played_games).order_by('-id')
    for game in played_games_uniq:
        if game.read_right(request_user):
            game.url = game.variation.thread.get_absolute_url
    return played_roles, played_games_uniq


class LoginTemplateView(TemplateView):
    @method_decorator(login_required)
    def get(self, *args, **kwargs):
        return super(LoginTemplateView, self).get(*args, **kwargs)


class PlayerProfileView(LoginTemplateView):
    template_name = 'profile/index.haml'
    
    @method_decorator(login_required)
    def post(self, *args, **kwargs):
        return self.get(*args, **kwargs)
    
    def get_context_data(self, **kwargs):
        request = self.request
        stats = Statistics(request.user)
        if stats.total_games > 0:
            played_roles, played_games = get_played(request.user)
            if played_roles.count() > 5:
                played_roles = played_roles[:5]    
        show_stories = (stats.story_admin > 0)
        show_games = (
            stats.total_games +
            GameGuest.objects.filter(user=request.user).count() +
            stats.games_admin > 0)

        if request.user.is_superuser:
            rankform = RankForm(
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
        return locals()


class PlayerPlayedView(LoginTemplateView):
    template_name = 'profile/played.haml'
    
    def get_context_data(self, **kwargs):
        played_roles, played_games = get_played(self.request.user)
        roles_on_page = 50
        return locals()


class PlayerUserProfileView(PlayerView):
    template_name = 'players/played.haml'

    def get_context_data(self, **kwargs):
        player = self.object
        played_roles, played_games = get_played(self.request.user, player)
        items_on_page = 50
        return locals()


class PlayerUploadedFilesView(LoginTemplateView):
    template_name = 'profile/files.haml'
    
    def get_context_data(self, **kwargs):
        return {'files': UploadedFile.objects.filter(user=self.request.user)}
