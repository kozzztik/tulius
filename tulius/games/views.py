import json

from django import urls
from django import http
from django import template
from django.apps import apps
from django.contrib import messages
from django.db.models import query_utils
from django.contrib.auth import decorators
from django.template import loader
from django.views import generic
from django.utils.translation import ugettext_lazy as _

from djfw import subviews
from djfw import views as djfw_views
from djfw.cataloging import core as cataloging

from tulius.stories import models as stories
from tulius.games import forms
from tulius.games import catalog
from tulius.games import models


gameforum_site = apps.get_app_config('gameforum').site


class MessageMixin:
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


# pylint: disable=too-many-branches
def set_edit(games, user):
    for game in games:
        game.text_hint = ''
        game.edit = game.edit_right(user)
        if game.edit:
            game.text_hint = _("You are admin of this game")
        if not user.is_anonymous:
            game.user_roles = stories.Role.objects.filter(
                variation=game.variation, user=user)
            for role in game.user_roles:
                role.text_url = urls.reverse(
                    'games:view_role', args=(role.pk,))
        if game.can_send_request(user):
            if game.sended_request(user):
                if game.user_roles.count() == 0:
                    game.cancel_request = True
                if not game.text_hint:
                    game.text_hint = _("You sended request to play this game")
            elif game.vacant_roles().count() > 0:
                game.request = True
                if not game.text_hint:
                    game.text_hint = _(
                        "This game is open for registration, "
                        "you can send request to play it")
            else:
                game.full = True
                if not game.text_hint:
                    game.text_hint = _("You can`t join this game, it is full")
        if game.read_right(user):
            game.enter = (game.status >= models.GAME_STATUS_IN_PROGRESS)
            game.full = False
            game.enter_url = urls.reverse('gameforum:game', args=(game.pk,))
            if not game.text_hint:
                if game.write_right(user):
                    game.text_hint = _("You participate in this game")
                else:
                    game.text_hint = _("You are a guest in this game")
    return games


class IndexView(generic.TemplateView):
    template_name = 'games/index.haml'

    def get_context_data(self, **kwargs):
        user = self.request.user
        return {
            'new_games': set_edit(models.Game.objects.new_games(user), user),
            'announced_games': set_edit(
                models.Game.objects.announced_games(user), user),
            'awaiting_start_games': set_edit(
                models.Game.objects.awaiting_start_games(user), user),
            'current_games': set_edit(
                models.Game.objects.current_games(user), user),
            'completed_games': set_edit(
                models.Game.objects.completed_games(user), user),
            'completed_open_games': set_edit(
                models.Game.objects.completed_open_games(user), user),
            'catalog_page': catalog.games_catalog_page(),
        }


class GamesListBase(generic.TemplateView):
    template_name = 'games/games_list.haml'
    page_name = ''
    proc_name = ''

    def process_games(self, games):
        pass

    def get_context_data(self, **kwargs):
        user = self.request.user
        proc = getattr(models.Game.objects, self.proc_name)
        games = set_edit(proc(user), user)
        self.process_games(games)
        return {
            'catalog_page': cataloging.CatalogPage(
                name=self.page_name,
                parent=catalog.index_catalog_page,
                is_index=True),
            'games': games,
        }


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
            game.online_roles = gameforum_site.core.get_online_roles(
                None, thread, False)


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
            pass


class CreateGame(MessageMixin, subviews.SubCreateView):
    model = models.Game
    form_class = forms.AddGameForm
    parent_model = stories.Variation
    template_name = 'games/add_game.haml'

    def form_valid(self, form):
        variation = self.parent_object
        if not variation.create_right(self.request.user):
            raise http.Http404()
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
        game.variation.thread = gameforum_site.core.copy_game_forum(
            game.variation, rolelinks, self.request.user)
        copy_file(game, story.card_image, game.card_image)
        copy_file(game, story.top_banner, game.top_banner)
        copy_file(game, story.bottom_banner, game.bottom_banner)
        admin = models.GameAdmin(game=game, user=self.request.user)
        admin.save()
        messages.success(self.request, _('game was successfully created'))
        return http.HttpResponseRedirect(game.get_edit_url())

    def get_context_data(self, **kwargs):
        context = super(CreateGame, self).get_context_data(**kwargs)
        context['catalog_page'] = cataloging.CatalogPage(
            name=_('create game'), parent=catalog.games_catalog_page())
        context['form_submit_title'] = _("add")
        return context


def get_game_page(game):
    return cataloging.CatalogPage(
        instance=game, parent=catalog.games_catalog_page(), is_index=True)


def role_text_read_right(role, user, game):
    if not game:
        return False
    if game.status == models.GAME_STATUS_COMPLETED_OPEN:
        return True
    if user.is_anonymous:
        return False
    if user.is_superuser or game.edit_right(user):
        return True
    if role.user == user and (
            game.status >= models.GAME_STATUS_REGISTRATION_COMPLETED):
        return True
    return (
        game.status in [
            models.GAME_STATUS_FINISHING, models.GAME_STATUS_COMPLETED]
        and game.read_right(user)
    )


class GameView(djfw_views.RightsDetailMixin, generic.DetailView):
    template_name = 'games/game.haml'
    model = models.Game

    def check_rights(self, obj, user):
        if obj.read_right(user):
            obj.enter_url = urls.reverse('gameforum:game', args=(obj.pk,))
        if obj.edit_right(user):
            obj.edit_url = obj.get_edit_url()
        obj.send_request = (
            obj.can_send_request(user) and not
            obj.sended_request(user))
        return obj.view_info_right(user)

    def get_context_data(self, **kwargs):
        game = self.object
        kwargs['catalog_page'] = get_game_page(game)
        roles = stories.Role.objects.filter(
            variation=game.variation, show_in_character_list=True
        ).exclude(deleted=True)
        for role in roles:
            if role_text_read_right(role, self.request.user, game):
                role.text_url = urls.reverse(
                    'games:view_role', args=(role.pk,))
        kwargs['roles'] = roles
        kwargs['authors'] = stories.StoryAuthor.objects.filter(
            story=game.variation.story)
        kwargs['materials'] = stories.AdditionalMaterial.objects.filter(
            (
                query_utils.Q(variation=game.variation) |
                query_utils.Q(story=game.variation.story)
            ) & query_utils.Q(admins_only=False))
        return super(GameView, self).get_context_data(**kwargs)


class GameRoleView(djfw_views.RightsDetailMixin, generic.DetailView):
    template_name = 'games/game_role.haml'
    model = stories.Role

    def check_rights(self, obj, user):
        game = obj.variation.game
        self.game = game
        self.game.edit = game.edit_right(user)
        if game.read_right(user):
            game.enter_url = urls.reverse('gameforum:game', args=(game.pk,))
        return role_text_read_right(obj, user, game)

    def get_context_data(self, **kwargs):
        kwargs['game'] = self.game
        game_page = get_game_page(self.game)
        kwargs['game_page'] = game_page
        kwargs['catalog_page'] = cataloging.CatalogPage(
            name=self.object.name, parent=game_page)
        return super(GameRoleView, self).get_context_data(**kwargs)


@decorators.login_required
def invite_player(
        request, game_id, template_name='games/game_edit/invite_form.haml'):
    success = 'error'
    error_text = ''
    game = None
    try:
        game = models.Game.objects.get(id=game_id)
    except:
        error_text = 'No such game %s' % (game_id,)
    if game and (not game.edit_right(request.user)):
        error_text = 'No rights on %s' % (game,)
    else:
        inviteform = forms.GameInviteForm(
            data=request.POST or None, variation=game.variation)
        if inviteform.is_valid():
            inv_user = inviteform.cleaned_data['user']
            inv_role = inviteform.cleaned_data['role']
            inv_message = inviteform.cleaned_data['message']
            if inv_role.variation.game == game:
                invites = models.GameInvite.objects.filter(
                    user=inv_user, role=inv_role,
                    status=models.GAME_INVITE_STATUS_NEW)
                if invites.count() == 0:
                    invite = models.GameInvite(
                        user=inv_user, role=inv_role, sender=request.user)
                    invite.save()
                if inv_message:
                    inv_user.send_pm(request.user, inv_message)
                success = 'success'
    t = loader.get_template(template_name)
    response = t.render(template.Context(locals()))
    return http.HttpResponse(
        json.dumps(
            {'response': str(response), 'result': success,
             'error_text': error_text}))


@decorators.login_required
def invite_accept(request, invite):
    if invite.user != request.user:
        raise http.Http404()
    invite.status = models.GAME_INVITE_STATUS_ACCEPTED
    models.GameInvite.objects.filter(role=invite.role).exclude(
        id=invite.id).update(status=models.GAME_INVITE_STATUS_OCCUPIED)
    invite.role.user = request.user
    invite.role.save()
    invite.save()


@decorators.login_required
def invite_decline(request, invite):
    if invite.user != request.user:
        raise http.Http404()
    invite.status = models.GAME_INVITE_STATUS_DECLINED
    invite.save()


class ChangeGameStoryView(djfw_views.RightsDetailMixin, generic.UpdateView):
    template_name = 'games/change_story.haml'
    model = models.Game
    form_class = forms.GameChangeStoryForm
    superuser_required = True

    def get_form_kwargs(self):
        return {'initial': {'story': self.object.variation.story},
                'data': self.request.POST or None}

    def form_valid(self, form):
        story = form.cleaned_data['story']
        variation = self.object.variation
        variation.story = story
        variation.save()
        roles = stories.Role.objects.filter(variation=variation)
        for role in roles:
            role.character = None
            role.avatar = None
            chars = stories.Character.objects.filter(
                story=story, name=role.name)
            if chars:
                role.character = chars[0]
                role.avatar = chars[0].avatar
            role.save()
        return http.HttpResponseRedirect(urls.reverse('games:index'))


class DeleteGame(djfw_views.RightsDetailMixin, generic.DeleteView):
    template_name = 'games/delete_game.haml'
    model = models.Game
    success_url = urls.reverse_lazy('games:index')

    def check_rights(self, obj, user):
        return user.is_superuser
