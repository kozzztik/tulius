from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.views.generic import TemplateView, DetailView, View
from django.contrib.auth.decorators import login_required
from django.db.models.query_utils import Q
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.template.loader import get_template
from django.template import Context
from django.db.models import Count
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.decorators import method_decorator
from djfw.bugtracker.models import Bug
from tulius.forum.models import UploadedFile, Comment, CommentLike
from tulius.stories.models import StoryAdmin, Role, Variation, StoryAuthor
from tulius.games.models import Game, GAME_STATUS_COMPLETED, GAME_STATUS_COMPLETED_OPEN, GameWinner, GameAdmin, GameInvite
from tulius.games.models import GAME_INVITE_STATUS_NEW, GameGuest, GAME_STATUS_IN_PROGRESS, GAME_STATUS_FINISHING
from tulius.games.views import set_edit, invite_accept, invite_decline
from tulius.gameforum import GAMEFORUM_SITE_ID, site as gameforum_site
from tulius.forum import site as forum_site
from tulius.models import User
from .models import stars
from .forms import SendMessageForm, PlayersFilterForm, PLAYERS_SORT_STORIES_AUTHORED,\
    PLAYERS_SORT_GAMES_PLAYED_INC, PLAYERS_SORT_GAMES_PLAYED_DEC, PLAYERS_SORT_REG_DATE, PLAYERS_SORT_ALPH,\
    ChangeEmailForm, ProfileSettingsForm, PersonalSettingsForm, RankForm, NotificationForm
from pm.models import PrivateMessage, PrivateTalking
import json
from events.models import UserNotification, Notification

stars.flush_stars_cache()

def filter_by_games(players):
    return players.filter(roles__variation__game__status__in=[GAME_STATUS_COMPLETED, GAME_STATUS_COMPLETED_OPEN]).annotate(
        games=Count('roles__variation__game', distinct=True))

def filter_by_stories(players):
    return players.annotate(stories=Count('authored_stories')).order_by('-stories')

class PlayersListView(TemplateView):
    template_name='players/player_list.haml'
    
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
    template_name='players/index.haml'
    
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
            rankform = RankForm(data=self.request.POST or None, instance=player)
            if self.request.method == 'POST':
                if rankform.is_valid():
                    rankform.save()
                    messages.success(self.request, _('rank was successfully updated'))
                else:
                    messages.error(self.request, _('there were some errors during form validation'))
        show_messages = (not user.is_anonymous()) and (player.id <> user.id)
        if show_messages:
            message_list_tmp = PrivateMessage.objects.talking(user, player)
            
            pre_unread_messages = PrivateMessage.objects.filter(receiver=user, is_read=False)
            pre_unread_messages_count = pre_unread_messages.count()
            
            unread = PrivateMessage.objects.filter(receiver=user, sender=player, is_read=False)
            unread_count = unread.count()
            count = 5
            if unread_count > 5 :
                count = unread_count
            message_list_tmp = message_list_tmp.order_by('-id')[:count].all()
            message_list = []
            for message in message_list_tmp:
                message_list = [message] + message_list
            unread.update(is_read=True)
            user.update_not_readed()
        if not user.is_anonymous():
            form = SendMessageForm()
        return locals()
    
class PlayerSendMessageView(View):
    @method_decorator(login_required)
    def post(self, request, player_id):
        player = get_object_or_404(User, is_active=True, pk=player_id)
        form = SendMessageForm(data=request.POST or None)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.receiver = player
            message.save()
            messages.success(request, _('message send'))
        else:
            messages.error(request, _('there were some errors during form validation'))
        return HttpResponseRedirect(reverse('players:player_details', args=(player.id,)) + '#pm_messages')
        
class PlayerHistoryView(TemplateView):
    template_name='players/player_history.haml'
    
    @method_decorator(login_required)
    def get(self, *args, **kwargs):
        return super(PlayerHistoryView, self).get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        player = get_object_or_404(User, is_active=True, pk=kwargs['player_id'])
        message_list = PrivateMessage.objects.talking(self.request.user, player)
        message_on_page = 50
        return locals()

class Statistics:
    def __init__(self, user):
        self.posts = Comment.objects.filter(user=user, plugin_id=None).count()
        self.game_posts = Comment.objects.filter(user=user, plugin_id=GAMEFORUM_SITE_ID).count()
        variation_ids = [role['variation'] for role in Role.objects.filter(user=user).values('variation').distinct()]
        variations = Variation.objects.filter(id__in=variation_ids)
        variations = variations.filter(game__status__in=[GAME_STATUS_COMPLETED, GAME_STATUS_COMPLETED_OPEN])
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
    played_roles = Role.objects.filter(user=user, variation__game__status__in=[GAME_STATUS_COMPLETED, GAME_STATUS_COMPLETED_OPEN]).order_by('-variation__game__id')
    for role in played_roles:
        if role.variation.game.read_right(request_user):
            role.variation.game.url = role.variation.thread.get_absolute_url
        played_games = [role.variation.game.id] + played_games
    played_games_uniq = Game.objects.filter(id__in=played_games).order_by('-id')
    for game in played_games_uniq:
        if game.read_right(request_user):
            game.url = game.variation.thread.get_absolute_url
    return played_roles, played_games_uniq
        
class LoginTemplateView(TemplateView):
    @method_decorator(login_required)
    def get(self, *args, **kwargs):
        return super(LoginTemplateView, self).get(*args, **kwargs)

class PlayerProfileView(LoginTemplateView):
    template_name='profile/index.haml'
    
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
        talkings = PrivateTalking.objects.filter(receiver=request.user)[:25]
        show_stories = (stats.story_admin > 0)
        show_games = (stats.total_games + GameGuest.objects.filter(user=request.user).count() + stats.games_admin > 0)
        email_form = ChangeEmailForm(request.user, request.POST)
        settings_form = ProfileSettingsForm(data=request.POST or None, instance=request.user)
        personal_settings_form = PersonalSettingsForm(data=request.POST or None, instance=request.user)
        new_invites = GameInvite.objects.filter(user=request.user, status=GAME_INVITE_STATUS_NEW)
        old_invites = GameInvite.objects.filter(user=request.user).exclude(status=GAME_INVITE_STATUS_NEW)
        
        if request.user.is_superuser:
            rankform = RankForm(data=request.POST or None, instance=request.user)
            if request.method == 'POST':
                if rankform.is_valid():
                    rankform.save()
                    messages.success(request, _('rank was successfully updated'))
                else:
                    messages.error(request, _('there were some errors during form validation'))
        return locals()

class PlayerPlayedView(LoginTemplateView):
    template_name='profile/played.haml'
    
    def get_context_data(self, **kwargs):
        played_roles, played_games = get_played(self.request.user)
        roles_on_page = 50
        return locals()

class PlayerUserProfileView(PlayerView):
    template_name='players/played.haml'
    def get_context_data(self, **kwargs):
        player = self.object
        played_roles, played_games = get_played(self.request.user, player)
        items_on_page = 50
        return locals()

class PostGroup:
    def __init__(self, name, game_id, comment):
        self.name = name
        self.id = game_id
        self.comments = [comment]
        self.forumsite = gameforum_site if game_id else forum_site
        
def get_post_group(groups, comment):
    if comment.plugin_id == GAMEFORUM_SITE_ID:
        variation = Variation.objects.get(thread__tree_id=comment.parent.tree_id)
        game_id = variation.id
        if variation.game:
            name = unicode(variation.game)
        else:
            name = unicode(variation)
        if comment.data1:
            comment.role = Role.objects.get(id=comment.data1)
    else:
        game_id = None
        name = _('Forums')
    for postgroup in groups:
        if postgroup.id == game_id:
            postgroup.comments += [comment]
            return groups
    resgroup = PostGroup(name, game_id, comment)
    groups += [resgroup]
    return groups

class PlayerFavoritesView(LoginTemplateView):
    template_name='profile/favorites.haml'
    
    def get_context_data(self, **kwargs):
        user = self.request.user
        likes = CommentLike.objects.select_related('comment').filter(user=user)
        comments = [like.comment for like in likes]
        for comment in comments:
            comment.view_user = user
        comments = [comment for comment in comments if comment.parent.read_right]
        groups = []
        for comment in comments:
            groups = get_post_group(groups, comment)
        block_trustmarks = True
        block_reply = True
        return locals()
        
class PlayerUploadedFilesView(LoginTemplateView):
    template_name='profile/files.haml'
    
    def get_context_data(self, **kwargs):
        return {'files': UploadedFile.objects.filter(user=self.request.user)}

class PlayerStoriesView(LoginTemplateView):
    template_name='profile/stories.haml'
    
    def get_context_data(self, **kwargs):
        return {'stories': [storyadmin.story for storyadmin in StoryAdmin.objects.filter(user=self.request.user)]}

class PlayerGamesView(LoginTemplateView):
    template_name='profile/games.haml'
    
    def get_context_data(self, **kwargs):
        user = self.request.user
        admined = [gameadmin.game.id for gameadmin in GameAdmin.objects.filter(user=user)]
        guested = [gameguest.game.id for gameguest in GameGuest.objects.filter(user=user)]
        played = [role.variation.game.id for role in Role.objects.filter(user=user, variation__game__isnull=False)]
        games = Game.objects.filter(Q(id__in=admined) | Q(id__in=guested) | Q(id__in=played))
        current_games = set_edit(games.filter(status__in=[GAME_STATUS_IN_PROGRESS, GAME_STATUS_FINISHING]), user)
        old_games = set_edit(games.filter(status__in=[GAME_STATUS_COMPLETED, GAME_STATUS_COMPLETED_OPEN]), user)
        admined_games = set_edit(games.filter(id__in=admined), user)
        return locals()

from tulius.bugs.views import issue_views as bug_views

class PlayerFoundBugsView(LoginTemplateView):
    template_name='profile/found_bugs.haml'
    
    def get_context_data(self, **kwargs):
        return {'bugs': Bug.objects.authored(self.request.user), 'urlizer': bug_views.urlizer}

class PlayerSettingsView(View):
    template_name='profile/settings_form.haml'
    
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        email_form = ChangeEmailForm(request.user, request.POST)
        settings_form = ProfileSettingsForm(data=request.POST or None, instance=request.user)
        personal_settings_form = PersonalSettingsForm(data=request.POST or None, instance=request.user)
        success = 'error'
        if email_form.is_valid() and settings_form.is_valid() and personal_settings_form.is_valid():
            if email_form.change_email:
                request.user.email = email_form.cleaned_data['email']
                request.user.save()
            if email_form.change_pass:
                request.user.set_password(email_form.cleaned_data['new_pass'])
                request.user.save()
            settings_form.save()
            personal_settings_form.save()
            success = 'success'
        t = get_template(self.template_name)
        response = t.render(Context(locals()))
        return HttpResponse(json.dumps({'response': unicode(response), 'result': success}))

class PlayerInviteBaseView(DetailView):
    model = GameInvite
    proc = None
    pk_url_kwarg = 'invite_id'
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        self.proc[0](request, self.get_object())
        return HttpResponseRedirect(reverse('players:profile') + '#invites')

class PlayerInviteAcceptView(PlayerInviteBaseView):
    proc = [invite_accept]
        
class PlayerInviteDeclineView(PlayerInviteBaseView):
    proc = [invite_decline]
    
class PlayerSubscriptionsView(LoginTemplateView):
    template_name='profile/subscriptions.haml'
    def get_context_data(self, **kwargs):
        notifications = [n for n in Notification.objects.all()]
        user_n = UserNotification.objects.filter(user=self.request.user)
        user_n = [n.notification for n in user_n if not n.enabled]
        forms = []
        for n in notifications:
            form = NotificationForm(prefix='n'+str(n.id), initial={'enabled': not n in user_n})
            form.notification = n
            forms += [form]
        return locals()
    @method_decorator(login_required)
    def post(self, request):
        notifications = [n for n in Notification.objects.all()]
        forms = []
        for n in notifications:
            form = NotificationForm(prefix='n'+str(n.id), data=request.POST)
            form.notification = n
            forms += [form]
        for form in forms:
            if form.is_valid():
                enabled = form.cleaned_data['enabled']
                if enabled:
                    UserNotification.objects.filter(user=self.request.user, notification=form.notification).delete()
                else:
                    n = UserNotification.objects.get_or_create(user=self.request.user, notification=form.notification)[0]
                    n.enabled = False
                    n.save()
        return HttpResponseRedirect(reverse('players:profile') + '#subscriptions')