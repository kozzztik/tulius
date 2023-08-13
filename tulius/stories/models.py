from datetime import timedelta

from django import urls
from django import dispatch
from django.db import models
from django.utils import html
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now
from django.contrib.auth import get_user_model

from djfw.common import CREATION_YEAR_CHOICES
from djfw.sortable.models import SortableModelMixin


User = get_user_model()


class Genre(models.Model):
    """
    Story genre
    """
    class Meta:
        verbose_name = _('genre')
        verbose_name_plural = _('genres')

    name = models.CharField(
        max_length=500,
        unique=False,
        verbose_name=_('name')
    )

    def __str__(self):
        return str(self.name)

    def get_absolute_url(self):
        return urls.reverse('stories:genre', kwargs={'genre_id': self.pk})

    def stories_count(self):
        return self.stories.all().count()

    def stories_list(self):
        val = ''
        for story in self.stories.all():
            val += '<a href="%s">%s</a><br />' % (
                story.get_absolute_url(), story.name)
        return val

    stories_count.short_description = _('stories')
    stories_list.short_description = _('stories')
    stories_list.allow_tags = True


class Story(models.Model):
    class Meta:
        verbose_name = _('story')
        verbose_name_plural = _('stories')

    name = models.CharField(
        max_length=200,
        default='',
        blank=False,
        null=False,
        verbose_name=_('name')
    )
    announcement = models.TextField(
        default='',
        blank=True,
        verbose_name=_('announcement'),
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
    creation_year = models.PositiveIntegerField(
        choices=CREATION_YEAR_CHOICES,
        verbose_name=_('creation year'),
    )
    genres = models.ManyToManyField(
        Genre,
        blank=True,
        verbose_name=_('genres'),
        related_name='stories',
    )
    card_image = models.FileField(
        null=True,
        blank=True,
        verbose_name=_('playing card image'),
        upload_to='stories/card_image',
    )
    top_banner = models.FileField(
        blank=True,
        null=True,
        verbose_name=_('top banner'),
        upload_to='stories/top_banner',
    )
    bottom_banner = models.FileField(
        blank=True,
        null=True,
        verbose_name=_('bottom banner'),
        upload_to='stories/bottom_banner',
    )
    hidden = models.BooleanField(
        default=True,
        verbose_name=_('hidden')
    )

    def __str__(self):
        return str(self.name)

    def get_absolute_url(self):
        return urls.reverse('stories:story', kwargs={'pk': self.pk})

    def get_edit_url(self):
        return urls.reverse('stories:edit_story_main', args=(self.pk,))

    def edit_right(self, user):
        if user.is_anonymous:
            return False
        if user.is_superuser:
            return True
        return StoryAdmin.objects.filter(user=user, story=self).count() > 0

    def create_right(self, user):
        if user.is_anonymous:
            return False
        if user.is_superuser:
            return True
        return self.admins.filter(user=user, create_game=True).count() > 0

    def get_variations(self):
        return Variation.objects.filter(story=self, game=None, deleted=False)


AVATAR_SAVE_SIZE = (200, 200)
AVATAR_SIZES = (
    (40, 40),
    (80, 80),
    (200, 200)
)
AVATAR_PATH = 'stories/avatars'
AVATAR_ALT_PATH = AVATAR_PATH + '-alt'


class Avatar(models.Model):
    class Meta:
        verbose_name = _('avatar')
        verbose_name_plural = _('avatars')

    story = models.ForeignKey(
        Story, models.PROTECT,
        blank=False,
        null=False,
        verbose_name=_('story'),
        related_name='avatars',
    )
    name = models.CharField(
        max_length=200,
        default='',
        blank=False,
        null=False,
        verbose_name=_('name')
    )
    image = models.FileField(
        upload_to=AVATAR_PATH,
        verbose_name=_('file')
    )

    def delete_data(self):
        try:
            self.image.delete()
        except:
            pass
        try:
            for alt in self.alternatives.all():
                alt.delete_data()
                alt.delete()
        except:
            pass

    def delete(self, using=None, keep_parents=False):
        self.delete_data()
        Character.objects.filter(avatar=self).update(avatar=None)
        Role.objects.filter(avatar=self).update(avatar=None)
        return super().delete(using=using, keep_parents=keep_parents)

    def __str__(self):
        return '%s' % (self.name,)

    def get_absolute_url(self):
        return urls.reverse('stories:avatar', args=(self.pk,))

    def get_delete_url(self):
        return urls.reverse('stories:delete_avatar', args=(self.pk,))


class AvatarAlternative(models.Model):
    class Meta:
        verbose_name = _('avatar alternative')
        verbose_name_plural = _('avatars alternaties')

    avatar = models.ForeignKey(
        Avatar, models.PROTECT,
        blank=False,
        null=False,
        verbose_name=_('avatar'),
        related_name='alternatives',
    )

    height = models.IntegerField(
        default=0,
        verbose_name=_('height'),
    )

    width = models.IntegerField(
        default=0,
        verbose_name=_('width'),
    )

    image = models.FileField(
        upload_to=AVATAR_ALT_PATH,
        verbose_name=_('file')
    )

    def __str__(self):
        return '%s %sx%s' % (self.avatar.name, self.height, self.width)

    def delete_data(self):
        try:
            self.image.delete()
        except:
            pass


CHAR_SEX_UNDEFINED = 0
CHAR_SEX_MALE = 1
CHAR_SEX_FEMALE = 2
CHAR_SEX_MIDDLE = 3
CHAR_SEX_PLUR = 4

CHAR_SEX_CHOICES = (
    (CHAR_SEX_UNDEFINED, _('Not defined')),
    (CHAR_SEX_MALE, _('Male')),
    (CHAR_SEX_FEMALE, _('Female')),
    (CHAR_SEX_MIDDLE, _('Middle')),
    (CHAR_SEX_PLUR, _('Plural')),
)


class Character(models.Model):
    class Meta:
        verbose_name = _('character')
        verbose_name_plural = _('characters')
        ordering = ['order', 'id']

    story = models.ForeignKey(
        Story, models.PROTECT,
        blank=False,
        null=False,
        verbose_name=_('story'),
        related_name='characters',
    )
    name = models.CharField(
        max_length=200,
        default='',
        blank=False,
        null=False,
        verbose_name=_('name')
    )
    order = models.IntegerField(
        default=0,
        blank=False,
        null=False,
        verbose_name=_('order'),
        editable=False
    )
    sex = models.SmallIntegerField(
        default=CHAR_SEX_UNDEFINED,
        verbose_name=_('sex'),
        choices=CHAR_SEX_CHOICES,
    )

    description = models.TextField(
        verbose_name=_('description'),
        blank=True,
        null=True,
    )
    avatar = models.ForeignKey(
        Avatar, models.PROTECT,
        blank=True,
        null=True,
        verbose_name=_('avatar'),
        related_name='characters',
    )
    show_in_character_list = models.BooleanField(
        default=False,
        verbose_name=_('show in character list')
    )

    def __str__(self):
        return str(self.name)

    def get_absolute_url(self):
        return urls.reverse('stories:character', args=(self.pk,))

    def get_info_url(self):
        return urls.reverse('stories:character_info', kwargs={'pk': self.pk})


class Variation(SortableModelMixin):
    class Meta:
        verbose_name = _('variation')
        verbose_name_plural = _('variations')
        ordering = ['order', 'id']

    objects = models.Manager()  # linters don't worry, be happy

    story = models.ForeignKey(
        Story, models.PROTECT,
        blank=False,
        null=False,
        verbose_name=_('story'),
        related_name='variations',
    )
    name = models.CharField(
        max_length=200,
        default='',
        blank=False,
        null=False,
        verbose_name=_('name')
    )
    description = models.TextField(
        verbose_name=_('description'),
        blank=True,
        null=True,
    )
    game = models.ForeignKey(
        'games.Game', models.PROTECT,
        verbose_name=_('game'),
        related_name='story_variation',
        blank=True,
        null=True,
    )

    thread = models.ForeignKey(
        'game_forum_threads.Thread', models.PROTECT,
        verbose_name=_('new forum'),
        related_name='variations',
        blank=True,
        null=True,
    )

    comments_count = models.PositiveIntegerField(
        default=0,
        blank=False,
        null=False,
        verbose_name=_('comments_count'),
    )

    deleted = models.BooleanField(
        default=False,
        verbose_name=_('deleted')
    )

    def __str__(self):
        return str(self.name)

    def get_absolute_url(self):
        return urls.reverse('stories:variation', args=(self.pk,))

    def edit_right(self, user):
        if self.game:
            return self.game.edit_right(user)
        return self.story.edit_right(user)

    def create_right(self, user):
        return self.story.create_right(user)

    def copy(self):
        old_id, self.pk = self.pk, None
        self.comments_count = 0
        self.save()
        rolelinks = {}
        for role in Role.objects.filter(
                variation__id=old_id).exclude(deleted=True):
            old_role = role.pk
            role.copy(self)
            rolelinks[old_role] = role
        for material in AdditionalMaterial.objects.filter(
                variation__id=old_id):
            material.copy(self)
        for illustration in Illustration.objects.filter(
                variation__id=old_id):
            illustration.copy(self)
        return rolelinks

    def delete(self, using=None, keep_parents=False):
        self.deleted = True
        self.save()

    def forumlink(self):
        return f'/play/variation/{self.pk}/'

    def get_roles(self):
        return Role.objects.filter(variation=self).exclude(deleted=True)

    def comments_count_inc(self, value):
        Variation.objects.filter(pk=self.pk).update(
            comments_count=models.F('comments_count') + value)
        self.comments_count += value

    _all_roles_cache = None

    @property
    def all_roles(self):
        if self._all_roles_cache is None:
            self._all_roles_cache = {
                role.id: role for role in
                self.roles.all().select_related('avatar')}
        return self._all_roles_cache

    def role_to_json(self, role_id, user, detailed=False):
        if role_id is None:
            return {
                'id': None,
                'title': '---',
                'url': None,
                'sex': None,
                'avatar': None,
                'online_status': None,
                'trust': None,
                'show_trust_marks': False,
            }
        return self.all_roles[role_id].to_json(user, detailed=detailed)


class Role(SortableModelMixin):
    class Meta:
        verbose_name = _('role')
        verbose_name_plural = _('roles')
        ordering = ['order', 'id']

    objects = models.Manager()  # linters don't worry, be happy

    variation = models.ForeignKey(
        Variation, models.PROTECT,
        blank=False,
        null=False,
        verbose_name=_('variation'),
        related_name='roles',
    )
    character = models.ForeignKey(
        Character, models.PROTECT,
        blank=True,
        null=True,
        verbose_name=_('character'),
        related_name='roles',
    )
    avatar = models.ForeignKey(
        Avatar, models.PROTECT,
        blank=True,
        null=True,
        verbose_name=_('avatar'),
        related_name='roles',
    )
    name = models.CharField(
        max_length=200,
        default='',
        blank=False,
        null=False,
        verbose_name=_('name')
    )
    sex = models.SmallIntegerField(
        default=CHAR_SEX_UNDEFINED,
        verbose_name=_('sex'),
        choices=CHAR_SEX_CHOICES,
    )
    description = models.TextField(
        verbose_name=_('description'),
        blank=True,
        null=True,
    )
    body = models.TextField(
        verbose_name=_('text'),
        blank=True,
        null=True,
    )
    show_in_character_list = models.BooleanField(
        default=False,
        verbose_name=_('show in character list')
    )
    show_in_online_character = models.BooleanField(
        default=True,
        verbose_name=_('show in online characters')
    )
    show_trust_marks = models.BooleanField(
        default=True,
        verbose_name=_('show trust marks')
    )
    user = models.ForeignKey(
        User, models.PROTECT,
        blank=True,
        null=True,
        related_name='roles',
        verbose_name=_('user')
    )
    requestable = models.BooleanField(
        default=True,
        verbose_name=_('requestable')
    )

    deleted = models.BooleanField(
        default=False,
        blank=False,
        null=False,
        verbose_name=_('deleted')
    )

    visit_time = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('visit time'),
    )

    comments_count = models.PositiveIntegerField(
        default=0,
        blank=False,
        null=False,
        verbose_name=_('comments count'),
    )

    trust_value = models.PositiveIntegerField(
        default=0,
        blank=False,
        null=False,
        verbose_name=_('trust value'),
    )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return urls.reverse('stories:role', args=(self.id,))

    def get_text_url(self):
        return urls.reverse('stories:role_text', args=(self.pk,))

    def is_online(self):
        if not self.visit_time:
            return False
        return self.visit_time > now() - timedelta(minutes=3)

    def copy(self, new_variation):
        self.id = None
        self.variation = new_variation
        self.comments_count = 0
        self.save()
        return True

    def to_json(self, user, detailed=False):
        data = {
            'id': self.id,
            'title': html.escape(self.name),
            'url': None,
        }
        if detailed:
            on = self.is_online() if self.show_in_online_character else None
            data.update({
                'sex': self.sex,
                'avatar': self.avatar.image.url if (
                    self.avatar and self.avatar.image) else '',
                'online_status': on,
                'owned': (
                    user.is_authenticated and (
                        self.user_id == user.pk)),
                'trust': self.trust_value if self.show_trust_marks else None,
                'show_trust_marks': self.show_trust_marks,
            })
        return data


class RoleDeleteMark(models.Model):
    class Meta:
        verbose_name = _('role delete mark')
        verbose_name_plural = _('roles delete marks')

    role = models.ForeignKey(
        Role, models.PROTECT,
        blank=False,
        null=False,
        verbose_name=_('role'),
        related_name='delete_marks',
    )
    user = models.ForeignKey(
        User, models.PROTECT,
        blank=False,
        null=False,
        verbose_name=_('user'),
        related_name='role_delete_marks',
    )
    description = models.TextField(
        verbose_name=_('description'),
        blank=True,
        null=True,
    )

    delete_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('created at'),
    )

    def __str__(self):
        return _("%(role)s deleted by %(user)s at %(time)s") % {
            'role': str(self.role), 'user': str(self.user),
            'time': self.delete_time}


class StoryAdmin(models.Model):
    class Meta:
        verbose_name = _('story admin')
        verbose_name_plural = _('story admins')
        unique_together = ('story', 'user')

    CREATE_CHOICES = (
        (False, _('No')),
        (True, _('Yes')),
    )
    story = models.ForeignKey(
        Story, models.PROTECT,
        blank=False,
        null=False,
        verbose_name=_('story'),
        related_name='admins',
    )
    user = models.ForeignKey(
        User, models.PROTECT,
        blank=False,
        null=False,
        verbose_name=_('user'),
        related_name='admined_stories',
    )
    create_game = models.BooleanField(
        default=False,
        verbose_name=_('create game'),
        choices=CREATE_CHOICES
    )

    def __str__(self):
        if self.user:
            if self.create_game:
                return "%s (%s)" % (self.user, str(_("games admin")))
            return str(self.user)
        return None


class StoryAuthor(models.Model):
    class Meta:
        verbose_name = _('story author')
        verbose_name_plural = _('story authors')
        unique_together = ('story', 'user')

    story = models.ForeignKey(
        Story, models.PROTECT,
        blank=False,
        null=False,
        verbose_name=_('story'),
        related_name='authors',
    )
    user = models.ForeignKey(
        User, models.PROTECT,
        blank=False,
        null=False,
        verbose_name=_('user'),
        related_name='authored_stories',
    )

    def __str__(self):
        if self.user:
            return str(self.user)
        return None


@dispatch.receiver(models.signals.post_delete, sender=StoryAuthor)
@dispatch.receiver(models.signals.post_save, sender=StoryAuthor)
def on_story_author_updates(instance, **_kwargs):
    User.objects.filter(pk=instance.user_id).update(
        stories_author=StoryAuthor.objects.filter(
            user_id=instance.user_id).count())


class AdditionalMaterial(models.Model):
    class Meta:
        verbose_name = _('additional material')
        verbose_name_plural = _('additional materials')

    objects = models.Manager()  # linters don't worry, be happy

    story = models.ForeignKey(
        Story, models.PROTECT,
        blank=True,
        null=True,
        verbose_name=_('story'),
        related_name='additional_materials',
    )

    variation = models.ForeignKey(
        Variation, models.PROTECT,
        blank=True,
        null=True,
        verbose_name=_('variation'),
        related_name='additional_materials',
    )

    name = models.CharField(
        max_length=500,
        unique=False,
        verbose_name=_('name')
    )

    body = models.TextField(
        default='',
        verbose_name=_('body')
    )

    admins_only = models.BooleanField(
        default=True,
        verbose_name=_('Hide in materials')
    )

    def __str__(self):
        return str(self.name)

    def get_absolute_url(self):
        if self.variation and self.variation.game:
            return urls.reverse('games:edit_material', args=(self.pk,))
        return urls.reverse('stories:edit_material', args=(self.pk,))

    def url(self):
        if self.variation and self.variation.game:
            return urls.reverse('games:material', args=(self.pk,))
        return urls.reverse('stories:material', args=(self.pk,))

    def delete_url(self):
        if self.variation and self.variation.game:
            return urls.reverse('games:material_delete', args=(self.pk,))
        return urls.reverse('stories:material_delete', args=(self.pk,))

    def edit_right(self, user):
        if self.story:
            return self.story.edit_right(user)
        if self.variation:
            return self.variation.edit_right(user)
        return False

    def read_right(self, user):
        if not self.admins_only:
            return True
        if self.story:
            return self.story.edit_right(user)
        if self.variation:
            return self.variation.edit_right(user)
        return False

    def copy(self, new_variation):
        self.id = None
        self.variation = new_variation
        self.save()
        return True


ILLUSTRATION_PATH = 'stories/illustrations/'


class Illustration(models.Model):
    objects = models.Manager()  # linters don't worry, be happy

    story = models.ForeignKey(
        Story, models.PROTECT,
        blank=True,
        null=True,
        verbose_name=_('story'),
        related_name='illustrations',
    )

    variation = models.ForeignKey(
        Variation, models.PROTECT,
        blank=True,
        null=True,
        verbose_name=_('variation'),
        related_name='illustrations',
    )

    name = models.CharField(
        max_length=500,
        unique=False,
        verbose_name=_('name')
    )

    admins_only = models.BooleanField(
        default=True,
        verbose_name=_('Hide in materials')
    )

    image = models.FileField(
        upload_to=ILLUSTRATION_PATH,
        verbose_name=_('image')
    )

    thumb = models.FileField(
        upload_to=ILLUSTRATION_PATH,
        verbose_name=_('thumb')
    )

    def __str__(self):
        return str(self.name)

    def get_absolute_url(self):
        if self.variation and self.variation.game:
            return urls.reverse('games:edit_illustration', args=(self.pk,))
        return urls.reverse('stories:edit_illustration', args=(self.pk,))

    def delete_url(self):
        if self.variation and self.variation.game:
            return urls.reverse('games:illustration_delete', args=(self.pk,))
        return urls.reverse('stories:illustration_delete', args=(self.pk,))

    def delete_data(self):
        try:
            self.image.delete()
        except:
            pass
        try:
            self.thumb.delete()
        except:
            pass

    def delete(self, using=None, keep_parents=False):
        self.delete_data()
        return super().delete(using=using, keep_parents=keep_parents)

    def edit_right(self, user):
        if self.story:
            return self.story.edit_right(user)
        if self.variation:
            return self.variation.edit_right(user)
        return False

    def _copy_file(self, source_path, dest):
        if source_path:
            try:
                with open(source_path, mode='wb') as source:
                    dest.save('%s.jpg' % (self.pk,), source)
            except:
                pass

    def copy(self, new_variation):
        old_file = self.image.name
        old_thumb = self.thumb.name
        self.id = None
        self.variation = new_variation
        self.save()
        self._copy_file(old_file, self.image)
        self._copy_file(old_thumb, self.image)
        return True
