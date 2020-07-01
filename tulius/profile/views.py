from django import http
from django import urls
from django.utils.translation import ugettext_lazy as _
from django.views import generic
from django.utils import decorators
from django.contrib import messages
from django.contrib.auth import decorators as auth_decorators
from django.contrib.auth import update_session_auth_hash
from django.db.models import query_utils

from tulius.events.models import UserNotification, Notification
from tulius.stories.models import StoryAdmin, Role
from tulius.games.views import invite_accept, invite_decline, set_edit
from tulius.games.models import Game, GAME_STATUS_COMPLETED, \
    GAME_STATUS_COMPLETED_OPEN, GameAdmin, GameInvite
from tulius.games.models import GAME_INVITE_STATUS_NEW, GameGuest, \
    GAME_STATUS_IN_PROGRESS, GAME_STATUS_FINISHING
from .forms import NotificationForm, ChangeEmailForm, ProfileSettingsForm, \
    PersonalSettingsForm


class Index(generic.TemplateView):
    template_name = 'base_vue.html'


class PlayerSettingsView(generic.TemplateView):
    template_name = 'profile/settings.haml'

    def get_context_data(self, **kwargs):
        kwargs['email_form'] = ChangeEmailForm(self.request.user, None)
        kwargs['personal_settings_form'] = ProfileSettingsForm(
            instance=self.request.user)
        kwargs['settings_form'] = PersonalSettingsForm(
            instance=self.request.user)
        return kwargs

    @decorators.method_decorator(auth_decorators.login_required)
    def post(self, request, *args, **kwargs):
        email_form = ChangeEmailForm(request.user, request.POST)
        settings_form = ProfileSettingsForm(
            data=request.POST or None, instance=request.user)
        personal_settings_form = PersonalSettingsForm(
            data=request.POST or None, instance=request.user)
        if (email_form.is_valid() and settings_form.is_valid() and
                personal_settings_form.is_valid()):
            if email_form.change_email:
                request.user.email = email_form.cleaned_data['email']
                request.user.save()
            if email_form.change_pass:
                request.user.set_password(email_form.cleaned_data['new_pass'])
                update_session_auth_hash(request, request.user)
                request.user.save()
            settings_form.save()
            personal_settings_form.save()
            messages.success(request, _('Settings changed'))
            return http.HttpResponseRedirect(urls.reverse('profile:settings'))
        return self.render_to_response(locals())


class LoginTemplateView(generic.TemplateView):
    @decorators.method_decorator(auth_decorators.login_required)
    def get(self, request, *args, **kwargs):
        return super(LoginTemplateView, self).get(request, *args, **kwargs)


class PlayerSubscriptionsView(LoginTemplateView):
    template_name = 'profile/subscriptions.haml'

    def get_context_data(self, **kwargs):
        notifications = [n for n in Notification.objects.all()]
        user_n = UserNotification.objects.filter(user=self.request.user)
        user_n = [n.notification for n in user_n if not n.enabled]
        forms = []
        for n in notifications:
            form = NotificationForm(
                prefix='n'+str(n.id), initial={'enabled': n not in user_n})
            form.notification = n
            forms += [form]
        return locals()

    @decorators.method_decorator(auth_decorators.login_required)
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
                    UserNotification.objects.filter(
                        user=self.request.user,
                        notification=form.notification).delete()
                else:
                    n = UserNotification.objects.get_or_create(
                        user=self.request.user,
                        notification=form.notification)[0]
                    n.enabled = False
                    n.save()
        return http.HttpResponseRedirect(urls.reverse('profile:subscriptions'))


class InvitesView(LoginTemplateView):
    template_name = 'profile/invites.haml'

    @decorators.method_decorator(auth_decorators.login_required)
    def post(self, *args, **kwargs):
        return self.get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs['new_invites'] = GameInvite.objects.filter(
            user=self.request.user, status=GAME_INVITE_STATUS_NEW)
        kwargs['old_invites'] = GameInvite.objects.filter(
            user=self.request.user).exclude(status=GAME_INVITE_STATUS_NEW)
        return kwargs


class PlayerInviteBaseView(generic.DetailView):
    model = GameInvite
    proc = None
    pk_url_kwarg = 'invite_id'

    @decorators.method_decorator(auth_decorators.login_required)
    def get(self, request, *args, **kwargs):
        self.proc[0](request, self.get_object())
        return http.HttpResponseRedirect(urls.reverse('profile:invites'))


class PlayerInviteAcceptView(PlayerInviteBaseView):
    proc = [invite_accept]


class PlayerInviteDeclineView(PlayerInviteBaseView):
    proc = [invite_decline]


class PlayerStoriesView(LoginTemplateView):
    template_name = 'profile/stories.haml'

    def get_context_data(self, **kwargs):
        return {'stories': [
            storyadmin.story for storyadmin in StoryAdmin.objects.filter(
                user=self.request.user)]}


class PlayerGamesView(LoginTemplateView):
    template_name = 'profile/games.haml'

    def get_context_data(self, **kwargs):
        user = self.request.user
        admined = [
            gameadmin.game.id for gameadmin in GameAdmin.objects.filter(
                user=user)]
        guested = [
            gameguest.game.id for gameguest in GameGuest.objects.filter(
                user=user)]
        played = [
            role.variation.game.id for role in Role.objects.filter(
                user=user, variation__game__isnull=False)]
        games = Game.objects.filter(
            query_utils.Q(id__in=admined) |
            query_utils.Q(id__in=guested) |
            query_utils.Q(id__in=played))
        current_games = set_edit(
            games.filter(
                status__in=[GAME_STATUS_IN_PROGRESS, GAME_STATUS_FINISHING]),
            user)
        old_games = set_edit(
            games.filter(
                status__in=[
                    GAME_STATUS_COMPLETED, GAME_STATUS_COMPLETED_OPEN]),
            user)
        admined_games = set_edit(games.filter(id__in=admined), user)
        return {
            'current_games': current_games,
            'admined_games': admined_games,
            'old_games': old_games,
        }


def request_user_json(request):
    auth = request.user.is_authenticated
    return {
        'is_anonymous': request.user.is_anonymous,
        'authenticated': request.user.is_authenticated,
        'superuser': request.user.is_superuser,
        'id': request.user.pk if auth else None,
        'compact_text': request.user.compact_text if auth else '',
        'username': request.user.username if auth else None,
        'rank': request.user.rank if auth else None,
        'full_stars': request.user.full_stars() if auth else [],
        'not_readed_messages':
            request.user.not_readed_messages if auth else None,
        'new_invites': len(request.user.new_invites()) if auth else None,
        'avatar':
            request.user.avatar.url if auth and request.user.avatar else
            '/static/tulius/img/blank_avatar.jpg',
        'hide_trustmarks': request.user.hide_trustmarks if auth else False,
    }
