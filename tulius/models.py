import re

from django import urls
from django import dispatch
from django.db import models
from django.contrib.auth import models as auth_models
from django.core.mail import send_mail
from django.core import validators
from django.utils import timezone
from django.utils import html
from django.utils.translation import ugettext_lazy as _

from tulius import signals
from tulius.core.autocomplete.models import add_autocomplete_widget
from tulius.vk.models import VK_Profile
from tulius.pm.signals import private_message_created
from djfw.wysibb.templatetags import bbcodes


USER_SEX_UNDEFINED = 0
USER_SEX_MALE = 1
USER_SEX_FEMALE = 2

USER_SEX_CHOICES = (
    (USER_SEX_UNDEFINED, _('Not defined')),
    (USER_SEX_MALE, _('Male')),
    (USER_SEX_FEMALE, _('Female')),
)

USER_GAME_INLINE_TIME = 0
USER_GAME_INLINE_POSTS = 1
USER_GAME_INLINE_CHOICES = (
    (USER_GAME_INLINE_TIME, _('Current time')),
    (USER_GAME_INLINE_POSTS, _('Messages count')),
)


class User(auth_models.PermissionsMixin, auth_models.AbstractBaseUser):
    username = models.CharField(
        _('username'), max_length=30, unique=True,
        help_text=_('Required. 30 characters or fewer. Letters, numbers and '
                    '@/./+/-/_ characters'),
        validators=[
            validators.RegexValidator(
                re.compile(r'^[\w.@+-]+$', re.U),
                _('Enter a valid username.'), 'invalid')
        ])
    email = models.EmailField(_('email address'), blank=True)
    is_staff = models.BooleanField(
        _('staff status'), default=False,
        help_text=_('Designates whether the user can log into this admin '
                    'site.'))
    is_active = models.BooleanField(
        _('active'), default=True,
        help_text=_('Designates whether this user should be treated as '
                    'active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    avatar = models.ImageField(
        upload_to='avatars',
        blank=True,
        null=True
    )
    rank = models.CharField(
        max_length=255,
        default='',
        blank=True,
        null=True,
        verbose_name=_('rank')
    )
    show_played_games = models.BooleanField(
        default=True,
        verbose_name=_('show played games')
    )
    show_played_characters = models.BooleanField(
        default=True,
        verbose_name=_('show played characters')
    )
    show_online_status = models.BooleanField(
        default=True,
        verbose_name=_('show on-line status')
    )
    hide_trustmarks = models.BooleanField(
        default=False,
        verbose_name=_('hide trustmarks')
    )
    signature = models.TextField(
        max_length=400,
        default='',
        blank=True,
        verbose_name=_('signature')
    )
    compact_text = models.BooleanField(
        default=False,
        verbose_name=_('compact text')
    )
    icq = models.CharField(
        default='',
        blank=True,
        max_length=12,
        verbose_name=_('ICQ')
    )
    skype = models.CharField(
        default='',
        blank=True,
        max_length=50,
        verbose_name=_('skype')
    )
    sex = models.SmallIntegerField(
        default=USER_SEX_UNDEFINED,
        verbose_name=_(u'sex'),
        choices=USER_SEX_CHOICES,
    )

    game_inline = models.SmallIntegerField(
        default=USER_GAME_INLINE_TIME,
        blank=False,
        verbose_name=_(u'Show in game'),
        choices=USER_GAME_INLINE_CHOICES,
    )
    animation_speed = models.PositiveIntegerField(
        default=1000,
        blank=False,
        verbose_name=_(u'Animation speed'),
    )

    vk_profile = models.ForeignKey(
        VK_Profile,
        models.PROTECT,
        blank=True,
        null=True
    )

    not_readed_messages = models.SmallIntegerField(
        default=0,
        blank=False,
        editable=False,
        verbose_name=_(u'Show in game'),
    )

    last_read_pm_id = models.PositiveIntegerField(
        default=0,
        blank=False,
        editable=False,
    )
    stories_author = models.PositiveIntegerField(
        default=0,
        blank=False,
        editable=False,
    )
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = auth_models.UserManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        v = self.username
        return u'%s' % (v, )

    def get_absolute_url(self):
        return urls.reverse(
            'players:player_details', kwargs={'player_id': self.pk})

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username

    def email_user(self, subject, message, from_email=None):
        send_mail(subject, message, from_email, [self.email])

    # TODO: refactor this. Make counter updated by signals
    # pylint: disable=C0415
    def full_stars(self):
        from tulius.stories.models import Variation, Role
        from tulius.games import models as game_models
        from tulius.players.models import stars

        self.full_stars_cache = getattr(self, 'full_stars_cache', None)
        if self.full_stars_cache is not None:
            return self.full_stars_cache
        self.full_stars_cache = 0
        variation_ids = [role['variation'] for role in Role.objects.filter(
            user=self).values('variation').distinct()]
        variations = Variation.objects.filter(id__in=variation_ids)
        games_played = variations.filter(
            game__status__in=[
                game_models.GAME_STATUS_COMPLETED,
                game_models.GAME_STATUS_COMPLETED_OPEN]).count()
        big_stars = int(games_played / 100)
        games_played -= big_stars * 100
        small_stars = 0
        for star in stars.stars_list:
            if star <= games_played:
                small_stars += 1
            else:
                break
        self.full_stars_cache = 'b' * big_stars + 's' * small_stars + 'e' * (
            stars.stars_count - small_stars)
        return self.full_stars_cache

    new_invites_cache = None

    def new_invites(self):
        from tulius.games.models import GAME_INVITE_STATUS_NEW, GameInvite
        if self.new_invites_cache is None:
            self.new_invites_cache = GameInvite.objects.filter(
                user=self, status=GAME_INVITE_STATUS_NEW)
        return self.new_invites_cache

    def send_pm(self, sender, body):
        from tulius.pm.models import PrivateMessage
        pm = PrivateMessage(sender=sender, receiver=self, body=body)
        pm.save()

    def update_not_readed(self):
        from tulius.pm.models import PrivateMessage
        count = PrivateMessage.objects.filter(
            receiver=self, is_read=False, removed_by_receiver=False).count()
        self.not_readed_messages = count
        last = PrivateMessage.objects.filter(
            receiver=self, is_read=True).order_by('-id')[:1]
        if last:
            self.last_read_pm_id = last[0].pk
        self.save()

    def to_json(self, detailed=False):
        data = {
            'id': self.pk,
            'title': html.escape(self.username),
            'url': self.get_absolute_url(),
        }
        if detailed:
            data.update({
                'sex': self.sex,
                'avatar': self.avatar.url if self.avatar else '',
                'full_stars': self.full_stars(),  # TODO optimize it
                'rank': html.escape(self.rank),
                'stories_author': self.stories_author,
                'signature': bbcodes.bbcode(self.signature),
            })
        signals.user_to_json.send(
            User, instance=self, response=data, detailed=detailed)
        return data


User.autocomplete_widget = add_autocomplete_widget(
    User, User.objects.all(), User.USERNAME_FIELD)


@dispatch.receiver(private_message_created)
def on_pm_create(sender, **_kwargs):
    sender.receiver.update_not_readed()
