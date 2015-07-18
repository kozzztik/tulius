from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib import messages
from django.http import Http404, HttpResponseRedirect
from django.http import HttpResponse
from django.template.loader import get_template
from django.template import Context
from django.views.generic import DeleteView
from django.views.generic.detail import DetailView
from djfw.subviews import SubCreateView
from django.views.generic.edit import UpdateView

from djfw.cataloging.core import CatalogPage
from djfw.views import RightsDetailMixin
from tulius.stories.models import Variation, AdditionalMaterial, StoryAuthor, Character
from tulius.gameforum import site as gameforum_site
from .forms import AddGameForm, GameInviteForm, GameChangeStoryForm
from .catalog import games_catalog_page, index_catalog_page
from .models import *
import json

class MessageMixin(object):
    error_message = _('there were some errors during form validation')
    success_message = ''
    
    def form_valid(self, form):
        response = super(MessageMixin, self).form_valid(form)
        if self.success_message:
            messages.success(self.request, self.success_message)
        return response
    
    def form_invalid(self, form):
        if self.error_message:
            messages.error(self.request, self.error_message)
        return super(MessageMixin, self).form_invalid(form)
    
def set_edit(games, user):
    for game in games:
        game.text_hint = ''
        game.edit = game.edit_right(user)
        if game.edit:
            game.text_hint = _("You are admin of this game")
        if not user.is_anonymous():
            game.user_roles = Role.objects.filter(variation=game.variation, user=user)
            for role in game.user_roles:
                role.text_url = reverse('games:view_role', args=(role.pk,))
        if game.can_send_request(user):
            if game.sended_request(user):
                if game.user_roles.count() == 0:
                    game.cancel_request = True
                if not game.text_hint:
                    game.text_hint = _("You sended request to play this game")
            elif game.vacant_roles().count() > 0:
                game.request = True
                if not game.text_hint:
                    game.text_hint = _("This game is open for registration, you can send request to play it")
            else:
                game.full = True
                if not game.text_hint:
                    game.text_hint = _("You can`t join this game, it is full")
        if game.read_right(user):
            game.enter = (game.status >= GAME_STATUS_IN_PROGRESS)
            game.full = False
            game.enter_url = reverse('gameforum:game', args=(game.pk,))
            if not game.text_hint:
                if game.write_right(user):
                    game.text_hint = _("You participate in this game")
                else:
                    game.text_hint = _("You are a guest in this game")
    return games
    
class IndexView(TemplateView):
    template_name='games/index.haml'
    
    def get_context_data(self, **kwargs):
        user = self.request.user
        context = {}
        context['new_games'] = set_edit(Game.objects.new_games(user), user)
        context['announced_games'] = set_edit(Game.objects.announced_games(user), user)
        context['awaiting_start_games'] = set_edit(Game.objects.awaiting_start_games(user), user)
        context['current_games'] = set_edit(Game.objects.current_games(user), user)
        context['completed_games'] = set_edit(Game.objects.completed_games(user), user)
        context['completed_open_games'] = set_edit(Game.objects.completed_open_games(user), user)
        context['catalog_page'] = games_catalog_page()    
        return context
    
class GamesListBase(TemplateView):
    template_name='games/games_list.haml'
    page_name = ''
    proc_name = ''
    
    def process_games(self, games):
        pass
    
    def get_context_data(self, **kwargs):
        user = self.request.user
        context = {}
        context['catalog_page'] = CatalogPage(name=self.page_name, parent=index_catalog_page, is_index=True)
        proc = getattr(Game.objects, self.proc_name)
        games = set_edit(proc(user), user)
        self.process_games(games)
        context['games'] = games
        return context
    
class AnnouncedGames(GamesListBase):
    page_name = _('Announced games')
    proc_name = 'new_games'
    
class RequestAcceptingGames(GamesListBase):
    page_name = _('Accepting requests')
    proc_name = 'announced_games'

class AwaitingStartGames(GamesListBase):
    page_name = _('Awaiting start')
    proc_name = 'awaiting_start_games'

class CurrentGames(GamesListBase):
    page_name = _('Current games')
    proc_name = 'current_games'
    def process_games(self, games):
        for game in games:
            thread = game.variation.thread
            thread.variation = game.variation
            game.online_roles = gameforum_site.core.get_online_roles(None, thread, False)
            
class CompletedOpenedGames(GamesListBase):
    page_name = _('Opened completed')
    proc_name = 'completed_open_games'

def copy_file(game, source, dest):
    if source.name:
        try:
            source.open()
            try:
                dest.save('%s.jpg' % (game.pk,), source)
            finally:
                source.close()
        except:
            True

class CreateGame(MessageMixin, SubCreateView):
    model = Game
    form_class = AddGameForm
    parent_model = Variation
    template_name='games/add_game.haml'
    
    def form_valid(self, form):
        variation = self.parent_object
        if not variation.create_right(self.request.user):
            raise Http404()
        with transaction.commit_on_success():
            game = form.save(commit=False)
            story = variation.story
            game.announcement = story.announcement
            game.announcement_preview = story.announcement_preview
            game.introduction = story.introduction
            game.variation = variation
            game.save()
            rolelinks = variation.copy()
            game.variation = variation
            game.variation.game = game
            game.variation.save()
            game.save()
            game.variation.thread = gameforum_site.core.copy_game_forum(game.variation, rolelinks, self.request.user)
            copy_file(game, story.card_image, game.card_image)
            copy_file(game, story.top_banner, game.top_banner)
            copy_file(game, story.bottom_banner, game.bottom_banner)
            admin = GameAdmin(game=game, user=self.request.user)
            admin.save()
        messages.success(self.request, _('game was successfully created'))
        return HttpResponseRedirect(game.get_edit_url())
        
    def get_context_data(self, **kwargs):
        context = super(CreateGame, self).get_context_data(**kwargs)
        context['catalog_page'] = CatalogPage(name=_('create game'), parent=games_catalog_page())
        context['form_submit_title'] =  _("add")
        return context
        
def get_game_page(game):
    return CatalogPage(instance=game, parent=games_catalog_page(), is_index=True)
    
def role_text_read_right(role, user, game):
    if not game:
        return False
    if game.status == GAME_STATUS_COMPLETED_OPEN:
        return True
    if user.is_anonymous():
        return False
    if user.is_superuser:
        return True
    if game.edit_right(user):
        return True
    if role.user == user and game.status >= GAME_STATUS_REGISTRATION_COMPLETED:
        return True
    return ((game.status in [GAME_STATUS_FINISHING, GAME_STATUS_COMPLETED]) and game.read_right(user))
    
class GameView(RightsDetailMixin, DetailView):
    template_name = 'games/game.haml'
    model = Game
    
    def check_rights(self, obj, user):
        if obj.read_right(user):
            obj.enter_url = reverse('gameforum:game', args=(obj.pk,))
        if obj.edit_right(user):
            obj.edit_url = obj.get_edit_url()
        obj.send_request = obj.can_send_request(user) and not obj.sended_request(user)
        return obj.view_info_right(user)
    
    def get_context_data(self, **kwargs):
        game = self.object
        kwargs['catalog_page'] = get_game_page(game) 
        roles = Role.objects.filter(variation=game.variation, show_in_character_list=True).exclude(deleted=True)
        for role in roles:
            if role_text_read_right(role, self.request.user, game):
                role.text_url = reverse('games:view_role', args=(role.pk,))
        kwargs['roles'] = roles
        kwargs['authors'] = StoryAuthor.objects.filter(story=game.variation.story)
        kwargs['materials'] = AdditionalMaterial.objects.filter(
            (Q(variation=game.variation) | Q(story=game.variation.story)) & Q(admins_only=False))
        return super(GameView, self).get_context_data(**kwargs)
    
class GameRoleView(RightsDetailMixin, DetailView):
    template_name = 'games/game_role.haml'
    model = Role
    
    def check_rights(self, obj, user):
        game = obj.variation.game
        self.game = game
        self.game.edit = game.edit_right(user)
        if game.read_right(user):
            game.enter_url = reverse('gameforum:game', args=(game.pk,))
        return role_text_read_right(obj, user, game)
    
    def get_context_data(self, **kwargs):
        kwargs['game'] = self.game
        game_page = get_game_page(self.game) 
        kwargs['game_page'] = game_page
        kwargs['catalog_page'] = CatalogPage(name=self.object.name, parent=game_page) 
        return super(GameRoleView, self).get_context_data(**kwargs)
    
@login_required
def invite_player(request, game_id, template_name='games/game_edit/invite_form.haml'):
    success = 'error'
    error_text = ''
    try:
        game = Game.objects.get(id=game_id)
    except:
        error_text = 'No such game %s' % (game_id,)
    if game and (not game.edit_right(request.user)):
        error_text = 'No rights on %s' % (game,)
    else:
        inviteform = GameInviteForm(data=request.POST or None, variation=game.variation)
        if inviteform.is_valid():
            inv_user = inviteform.cleaned_data['user']
            inv_role = inviteform.cleaned_data['role']
            inv_message = inviteform.cleaned_data['message']
            if inv_role.variation.game == game:
                invites = GameInvite.objects.filter(user=inv_user, role=inv_role, status=GAME_INVITE_STATUS_NEW)
                if invites.count() == 0:
                    invite = GameInvite(user=inv_user, role=inv_role, sender=request.user)
                    invite.save()
                if inv_message:
                    inv_user.send_pm(request.user, inv_message)
                success = 'success'
    t = get_template(template_name)
    response = t.render(Context(locals()))
    return HttpResponse(json.dumps({'response': unicode(response), 'result': success, 'error_text': error_text}))

@login_required
def invite_accept(request, invite):
    if invite.user <> request.user:
        raise Http404()
    invite.status = GAME_INVITE_STATUS_ACCEPTED
    GameInvite.objects.filter(role=invite.role).exclude(id=invite.id).update(status=GAME_INVITE_STATUS_OCCUPIED)
    invite.role.user = request.user
    invite.role.save()
    invite.save()
    
@login_required
def invite_decline(request, invite):
    if invite.user <> request.user:
        raise Http404()
    invite.status = GAME_INVITE_STATUS_DECLINED
    invite.save()
    
class ChangeGameStoryView(RightsDetailMixin, UpdateView):
    template_name = 'games/change_story.haml'
    model = Game
    form_class = GameChangeStoryForm
    superuser_required = True
    
    def get_form_kwargs(self):
        return {'initial': {'story': self.object.variation.story}, 
                'data': self.request.POST or None}
    
    def form_valid(self, form):
        story = form.cleaned_data['story']
        with transaction.commit_on_success():
            variation = self.object.variation
            variation.story = story
            variation.save()
            roles = Role.objects.filter(variation=variation)
            for role in roles:
                role.character = None
                role.avatar = None
                chars = Character.objects.filter(story=story, name=role.name)
                if chars:
                    role.character = chars[0]
                    role.avatar = chars[0].avatar
                role.save()
        return HttpResponseRedirect(reverse('games:index'))

class DeleteGame(RightsDetailMixin, DeleteView):
    template_name = 'games/delete_game.haml'
    model = Game
    success_url = reverse_lazy('games:index')
    
    def check_rights(self, obj, user):
        return user.is_superuser