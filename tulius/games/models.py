from django import urls
from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models.query_utils import Q
from django.utils.translation import gettext_lazy as _

from tulius.stories.models import Role
from .signals import game_status_changed


User = get_user_model()


class Skin(models.Model):
    class Meta:
        verbose_name = _('skin')
        verbose_name_plural = _('skins')

    name = models.CharField(
        max_length=500,
        unique=False,
        verbose_name=_('name')
    )
    description = models.TextField(
        verbose_name=_('description'),
        blank=True,
        null=True,
    )


GAME_STATUS_NEW = 1
GAME_STATUS_OPEN_FOR_REGISTRATION = 2
GAME_STATUS_REGISTRATION_COMPLETED = 3
GAME_STATUS_IN_PROGRESS = 4
GAME_STATUS_FINISHING = 5
GAME_STATUS_COMPLETED = 6
GAME_STATUS_COMPLETED_OPEN = 7

GAME_STATUS_CHOICES = (
    (GAME_STATUS_NEW, _('new')),
    (GAME_STATUS_OPEN_FOR_REGISTRATION, _('open for registration')),
    (GAME_STATUS_REGISTRATION_COMPLETED, _('registration completed')),
    (GAME_STATUS_IN_PROGRESS, _('in progress')),
    (GAME_STATUS_FINISHING, _('finishing')),
    (GAME_STATUS_COMPLETED, _('completed')),
    (GAME_STATUS_COMPLETED_OPEN, _('completed and open')),
)


class GameManager(models.Manager):

    def any_completed(self):
        return self.filter(
            Q(status=GAME_STATUS_COMPLETED) | Q(
                status=GAME_STATUS_COMPLETED_OPEN)
        )

    def current(self):
        return self.filter(status=GAME_STATUS_IN_PROGRESS)

    def awaits_start(self):
        return self.filter(status=GAME_STATUS_REGISTRATION_COMPLETED)

    def completed_by_player(self, player):
        games = self.any_completed().filter(characters__user=player)
        for game in games:
            game.characters = game.characters.filter(user=player)
            game.winner_characters = game.winners.filter(user=player)
        return games

    def currently_played_by_player(self, player):
        return self.current().filter(characters__user=player)

    def player_is_going_to_play(self, player):
        return self.awaits_start().filter(characters__user=player)

    def won_by_user(self, player):
        games = self.any_completed().filter(winners__user=player)
        for game in games:
            game.characters = game.characters.filter(user=player)
            game.winner_characters = game.winners.filter(user=player)
        return games

    def new_games(self, user, announce=False):
        games = self.filter(status=GAME_STATUS_NEW, deleted=False)
        if announce:
            games = games.filter(show_announcement=True)
        return [game for game in games if game.view_info_right(user)]

    def announced_games(self, user, announce=False):
        games = self.filter(
            status=GAME_STATUS_OPEN_FOR_REGISTRATION, deleted=False)
        if announce:
            games = games.filter(show_announcement=True)
        return [game for game in games if game.view_info_right(user)]

    def awaiting_start_games(self, user, check_read=False, announce=False):
        games = self.filter(
            status=GAME_STATUS_REGISTRATION_COMPLETED, deleted=False)
        if announce:
            games = games.filter(show_announcement=True)
        return [
            game for game in games if game.view_info_right(user, check_read)]

    def current_games(self, user, check_read=False, announce=False):
        games = self.filter(
            Q(status=GAME_STATUS_IN_PROGRESS) | Q(
                status=GAME_STATUS_FINISHING)
        ).filter(deleted=False)
        if announce:
            games = games.filter(show_announcement=True)
        return [
            game for game in games if game.view_info_right(user, check_read)]

    def completed_games(self, user, check_read=False):
        if user.is_superuser:
            games = self.filter(status=GAME_STATUS_COMPLETED, deleted=False)
        elif user.is_anonymous:
            games = []
        else:
            guested = GameGuest.objects.filter(
                user=user, game__status=GAME_STATUS_COMPLETED,
                game__deleted=False).select_related('game')
            guested = [guest.game for guest in guested]
            admined = GameAdmin.objects.filter(
                user=user, game__status=GAME_STATUS_COMPLETED,
                game__deleted=False).select_related('game')
            admined = [admin.game for admin in admined]
            played = Role.objects.filter(
                user=user,
                variation__game__status=GAME_STATUS_COMPLETED,
                variation__game__deleted=False
            ).select_related('variation__game')
            played = [role.variation.game for role in played]
            games = guested + admined + played
            # delete duplicates
            games_list = {}
            for game in games:
                games_list[game.id] = game
            games = list(games_list.values())
            games.sort(key=lambda game: game.id, reverse=True)
        return games

    def completed_open_games(self, user):
        games = self.filter(
            status=GAME_STATUS_COMPLETED_OPEN, deleted=False).order_by('-id')
        return games


class Game(models.Model):
    """
    Game
    """
    class Meta:
        verbose_name = _('game')
        verbose_name_plural = _('games')

    objects = GameManager()

    variation = models.ForeignKey(
        'stories.Variation', models.PROTECT,
        null=False,
        blank=False,
        verbose_name=_('variation'),
        related_name='games',
    )
    serial_number = models.PositiveIntegerField(
        verbose_name=_('serial number'),
    )
    name = models.CharField(
        max_length=200,
        default='',
        blank=False,
        null=False,
        verbose_name=_('name')
    )
    status = models.SmallIntegerField(
        default=GAME_STATUS_NEW,
        verbose_name=_('status'),
        choices=GAME_STATUS_CHOICES,
    )
    announcement = models.TextField(
        default='',
        blank=True,
        verbose_name=_('announcement')
    )
    announcement_preview = models.TextField(
        default='',
        blank=True,
        verbose_name=_('announcement preview')
    )
    short_comment = models.CharField(
        max_length=500,
        default='',
        blank=True,
        verbose_name=_('short comment')
    )
    introduction = models.TextField(
        default='',
        blank=True,
        verbose_name=_('introduction'),

    )
    requests_text = models.TextField(
        default='',
        blank=True,
        verbose_name=_('requests text'),

    )
    card_image = models.FileField(
        null=True,
        blank=True,
        verbose_name=_('playing card image'),
        upload_to='games/card_image',
    )
    top_banner = models.FileField(
        blank=True,
        null=True,
        verbose_name=_('top banner'),
        upload_to='games/top_banner',
    )
    bottom_banner = models.FileField(
        blank=True,
        null=True,
        verbose_name=_('bottom banner'),
        upload_to='games/bottom_banner',
    )
    show_announcement = models.BooleanField(
        default=True,
        verbose_name=_('show announcement'),
    )
    skin = models.ForeignKey(
        Skin, models.PROTECT,
        verbose_name=_('skin'),
        related_name='games',
        blank=True,
        null=True,
    )

    deleted = models.BooleanField(
        default=False,
        verbose_name=_('deleted')
    )

    def status_as_text(self):
        for choice in GAME_STATUS_CHOICES:
            if choice[0] == self.status:
                return choice[1]
        return ''

    def edit_right(self, user):
        if user.is_anonymous:
            return False
        if user.is_superuser:
            return True
        users = GameAdmin.objects.filter(game=self, user=user)
        return users.count() > 0

    def write_right(self, user):
        if user.is_anonymous:
            return False
        if user.is_superuser:
            return True
        if self.edit_right(user):
            return True
        if self.status < GAME_STATUS_IN_PROGRESS:
            return False
        roles = Role.objects.filter(variation=self.variation, user=user)
        return roles.count() > 0

    def get_assigned_users(self):
        return [
            role.user for role in Role.objects.filter(
                variation=self.variation) if role.user]

    def read_right(self, user):
        if self.status == GAME_STATUS_COMPLETED_OPEN:
            return True
        if user.is_anonymous:
            return False
        if user.is_superuser:
            return True
        if self.write_right(user):
            return True
        users = GameGuest.objects.filter(game=self, user=user)
        if users.count() > 0:
            return True
        return len(users) > 0

    def view_info_right(self, user, force_check_read=False):
        if self.show_announcement and (not force_check_read):
            return True
        return self.read_right(user)

    def is_finishing(self):
        return self.status == GAME_STATUS_FINISHING

    def get_absolute_url(self):
        return urls.reverse('games:game', kwargs={'pk': self.pk})

    def get_edit_url(self):
        return urls.reverse(
            'games:edit_game_main', kwargs={'game_id': self.pk})

    def get_request_url(self):
        return urls.reverse('games:game_request', kwargs={'game_id': self.pk})

    def get_cancel_request_url(self):
        return urls.reverse(
            'games:cancel_game_request', kwargs={'game_id': self.pk})

    def __str__(self):
        return '%s - %d' % (self.name, int(self.serial_number))

    def clean(self):
        super().clean()
        if not self.serial_number:
            raise ValidationError(_('Specify game serial number'))
        if not self.variation_id:
            return
        games = Game.objects.filter(
            variation__story=self.variation.story,
            serial_number=self.serial_number, deleted=False)
        if games:
            for game in games:
                if game.id != self.id:
                    raise ValidationError(
                        _('Game serial number must be unique in story. This '
                          'number of game ') + str(game) + '.')

    def can_send_request(self, user):
        return (
            self.status == GAME_STATUS_OPEN_FOR_REGISTRATION) and (
                not user.is_anonymous)

    def sended_request(self, user):
        return RoleRequest.objects.filter(game=self, user=user).count() > 0

    def vacant_roles(self):
        return Role.objects.filter(variation=self.variation, user=None)

    def delete(self, using=None, keep_parents=False):
        self.deleted = True
        self.save()

    def save(
            self, force_insert=False, force_update=False, using=None,
            update_fields=None):
        was_none = self.id is None
        old_self = None
        if not was_none:
            old_self = Game.objects.select_for_update().get(id=self.id)

        super().save(
            force_insert=force_insert, force_update=force_update, using=using,
            update_fields=update_fields)
        if old_self:
            if old_self.status != self.status:
                game_status_changed.send(
                    self, old_status=old_self.status,
                    new_status=self.status)


class GameAdmin(models.Model):
    """
    Game admin
    """
    class Meta:
        verbose_name = _('game admin')
        verbose_name_plural = _('game admins')
        unique_together = ('game', 'user')

    game = models.ForeignKey(
        Game, models.PROTECT,
        null=False,
        blank=False,
        verbose_name=_('game'),
        related_name='admins',
    )
    user = models.ForeignKey(
        User, models.PROTECT,
        null=False,
        blank=False,
        verbose_name=_('user'),
        related_name='admined_games',
    )


class GameGuest(models.Model):
    """
    Game guest
    """
    class Meta:
        verbose_name = _('game guest')
        verbose_name_plural = _('game guests')
        unique_together = ('game', 'user')

    game = models.ForeignKey(
        Game, models.PROTECT,
        null=False,
        blank=False,
        verbose_name=_('game'),
        related_name='guests',
    )
    user = models.ForeignKey(
        User, models.PROTECT,
        null=False,
        blank=False,
        verbose_name=_('user'),
        related_name='guested_games',
    )


class GameWinner(models.Model):
    """
    Game winner
    """
    class Meta:
        verbose_name = _('game winner')
        verbose_name_plural = _('game winners')
        # unique_together = ('game', 'new_user') #not supported by old games

    game = models.ForeignKey(
        Game, models.PROTECT,
        null=False,
        blank=False,
        verbose_name=_('game'),
        related_name='winners',
    )
    user = models.ForeignKey(
        User, models.PROTECT,
        null=False,
        blank=False,
        verbose_name=_('user'),
        related_name='winned_games',
    )


class RoleRequest(models.Model):
    """
    Game role request
    """
    class Meta:
        verbose_name = _('role request')
        verbose_name_plural = _('role requests')

    objects = models.Manager()  # linters don't worry, be happy

    game = models.ForeignKey(
        Game, models.PROTECT,
        null=False,
        blank=False,
        verbose_name=_('game'),
        related_name='role_requests',
    )
    user = models.ForeignKey(
        User, models.PROTECT,
        null=False,
        blank=False,
        verbose_name=_('user'),
        related_name='requested_games',
    )

    body = models.TextField(
        default='',
        verbose_name=_('text')
    )

    def __str__(self):
        return '%s - %s' % (str(self.user), str(self.game))


class RoleRequestSelection(models.Model):
    """
    Game role request selected role
    """
    class Meta:
        verbose_name = _('role request selection')
        verbose_name_plural = _('role request selections')
        unique_together = ('role_request', 'role')

    role_request = models.ForeignKey(
        RoleRequest, models.PROTECT,
        null=False,
        blank=False,
        verbose_name=_('role request'),
        related_name='selections',
    )

    prefer_order = models.PositiveIntegerField(
        verbose_name=_('prefer order'),
    )

    role = models.ForeignKey(
        'stories.Role', models.PROTECT,
        null=False,
        blank=False,
        verbose_name=_('role'),
        related_name='requests',
    )


class RequestQuestion(models.Model):
    """
    Game role request question
    """
    class Meta:
        verbose_name = _('request question')
        verbose_name_plural = _('request questions')

    game = models.ForeignKey(
        Game, models.PROTECT,
        null=False,
        blank=False,
        verbose_name=_('game'),
        related_name='request_questions',
    )
    question = models.CharField(
        max_length=500,
        default='',
        blank=False,
        null=False,
        verbose_name=_('question')
    )

    def __str__(self):
        return str(self.question)


class RequestQuestionAnswer(models.Model):
    """
    Game role request question
    """
    class Meta:
        verbose_name = _('request question answer')
        verbose_name_plural = _('request question answers')

    role_request = models.ForeignKey(
        RoleRequest, models.PROTECT,
        null=False,
        blank=False,
        verbose_name=_('role request'),
        related_name='answers',
    )
    question = models.ForeignKey(
        RequestQuestion, models.PROTECT,
        null=False,
        blank=False,
        verbose_name=_('answer'),
        related_name='answers',
    )
    answer = models.CharField(
        max_length=500,
        blank=False,
        null=False,
        verbose_name=_('answer')
    )


GAME_INVITE_STATUS_NEW = 1
GAME_INVITE_STATUS_ACCEPTED = 2
GAME_INVITE_STATUS_DECLINED = 3
GAME_INVITE_STATUS_OCCUPIED = 4

GAME_INVITE_STATUS_CHOICES = (
    (GAME_INVITE_STATUS_NEW, _('new invite')),
    (GAME_INVITE_STATUS_ACCEPTED, _('accepted invite')),
    (GAME_INVITE_STATUS_DECLINED, _('declined invite')),
    (GAME_INVITE_STATUS_OCCUPIED, _('occupied invite')),
)


class GameInvite(models.Model):
    """
    Game role user invite
    """
    class Meta:
        verbose_name = _('game invite')
        verbose_name_plural = _('game invites')
        ordering = ['-id']

    role = models.ForeignKey(
        'stories.Role', models.PROTECT,
        null=False,
        blank=False,
        verbose_name=_('role'),
        related_name='invites',
    )

    user = models.ForeignKey(
        User, models.PROTECT,
        null=False,
        blank=False,
        verbose_name=_('user'),
        related_name='invites',
    )

    status = models.SmallIntegerField(
        default=GAME_INVITE_STATUS_NEW,
        verbose_name=_('status'),
        choices=GAME_INVITE_STATUS_CHOICES,
    )

    sender = models.ForeignKey(
        User, models.PROTECT,
        null=False,
        blank=False,
        verbose_name=_('sender'),
        related_name='sended_invites',
    )

    create_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('created at'),
    )

    def status_as_text(self):
        for choice in GAME_INVITE_STATUS_CHOICES:
            if choice[0] == self.status:
                return choice[1]
        return ''
