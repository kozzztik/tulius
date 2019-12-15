from django import http
from django import urls
from django.apps import apps
from django.utils.translation import ugettext_lazy as _
from django.views import generic
from django.utils import decorators
from django.contrib import messages
from django.contrib.auth import decorators as auth_decorators
from django.db.models import query_utils

from tulius.events.models import UserNotification, Notification
from tulius.forum.models import CommentLike
from tulius.stories.models import StoryAdmin, Role, Variation
from tulius.games.views import invite_accept, invite_decline, set_edit
from tulius.games.models import Game, GAME_STATUS_COMPLETED, \
    GAME_STATUS_COMPLETED_OPEN, GameAdmin, GameInvite
from tulius.games.models import GAME_INVITE_STATUS_NEW, GameGuest, \
    GAME_STATUS_IN_PROGRESS, GAME_STATUS_FINISHING
from .forms import NotificationForm, ChangeEmailForm, ProfileSettingsForm, \
    PersonalSettingsForm


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


class PostGroup:
    def __init__(self, name, game_id, comment):
        self.name = name
        self.id = game_id
        self.comments = [comment]
        app = 'gameforum' if game_id else 'forum'
        self.forumsite = apps.get_app_config(app).site


class PlayerFavoritesView(LoginTemplateView):
    template_name = 'profile/favorites.haml'

    @staticmethod
    def get_post_group(groups, comment):
        config = apps.get_app_config('gameforum')
        if comment.plugin_id == config.GAME_FORUM_SITE_ID:
            variation = Variation.objects.get(
                thread__tree_id=comment.parent.tree_id)
            game_id = variation.id
            if variation.game:
                name = str(variation.game)
            else:
                name = str(variation)
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

    def get_context_data(self, **kwargs):
        user = self.request.user
        likes = CommentLike.objects.select_related('comment').filter(user=user)
        comments = [like.comment for like in likes]
        for comment in comments:
            comment.view_user = user
        comments = [
            comment for comment in comments if comment.parent.read_right]
        groups = []
        for comment in comments:
            self.get_post_group(groups, comment)
        block_trustmarks = True
        block_reply = True
        return {
            'groups': groups,
            'block_trustmarks': block_trustmarks,
            'block_reply': block_reply,
        }


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
