from datetime import timedelta

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now
from django.contrib.auth import get_user_model

from djfw.common import CREATION_YEAR_CHOICES
from djfw.sortable.models import SortableModelMixin
from tulius.forum.models import Thread


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
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return 'stories:genre', (), {'genre_id': self.id}

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
        verbose_name = _(u'story')
        verbose_name_plural = _(u'stories')

    name = models.CharField(
        max_length=200,
        default='',
        blank=False,
        null=False,
        verbose_name=_(u'name')
    )
    announcement = models.TextField(
        default='',
        blank=True,
        verbose_name=_(u'announcement'),
    )
    announcement_preview = models.TextField(
        default='',
        blank=True,
        verbose_name=_(u'announcement preview')
    )
    short_comment = models.CharField(
        max_length=500,
        default='',
        blank=True,
        verbose_name=_(u'short comment')
    )
    introduction = models.TextField(
        default='',
        blank=True,
        verbose_name=_(u'introduction'),
    )
    creation_year = models.PositiveIntegerField(
        choices=CREATION_YEAR_CHOICES,
        verbose_name=_(u'creation year'),
    )
    genres = models.ManyToManyField(
        Genre,
        blank=True,
        verbose_name=_(u'genres'),
        related_name='stories',
    )
    card_image = models.FileField(
        null=True,
        blank=True,
        verbose_name=_(u'playing card image'),
        upload_to='stories/card_image',
    )
    top_banner = models.FileField(
        blank=True,
        null=True,
        verbose_name=_(u'top banner'),
        upload_to='stories/top_banner',
    )
    bottom_banner = models.FileField(
        blank=True,
        null=True,
        verbose_name=_(u'bottom banner'),
        upload_to='stories/bottom_banner',
    )
    hidden = models.BooleanField(
        default=True,
        verbose_name=_(u'hidden')
    )

    def __str__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return 'stories:story', (), {'pk': self.id}

    @models.permalink
    def get_edit_url(self):
        return 'stories:edit_story_main', (self.id,), {}

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
        verbose_name = _(u'avatar')
        verbose_name_plural = _(u'avatars')

    story = models.ForeignKey(
        Story, models.PROTECT,
        blank=False,
        null=False,
        verbose_name=_(u'story'),
        related_name='avatars',
    )
    name = models.CharField(
        max_length=200,
        default='',
        blank=False,
        null=False,
        verbose_name=_(u'name')
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
        return super(Avatar, self).delete(
            using=using, keep_parents=keep_parents)

    def __str__(self):
        return '%s' % (self.name,)

    @models.permalink
    def get_absolute_url(self):
        return 'stories:avatar', (self.id,), {}

    @models.permalink
    def get_delete_url(self):
        return 'stories:delete_avatar', (self.id, ), {}


class AvatarAlternative(models.Model):
    class Meta:
        verbose_name = _(u'avatar alternative')
        verbose_name_plural = _(u'avatars alternaties')

    avatar = models.ForeignKey(
        Avatar, models.PROTECT,
        blank=False,
        null=False,
        verbose_name=_(u'avatar'),
        related_name='alternatives',
    )

    height = models.IntegerField(
        default=0,
        verbose_name=_(u'height'),
    )

    width = models.IntegerField(
        default=0,
        verbose_name=_(u'width'),
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
        verbose_name = _(u'character')
        verbose_name_plural = _(u'characters')
        ordering = ['order', 'id']

    story = models.ForeignKey(
        Story, models.PROTECT,
        blank=False,
        null=False,
        verbose_name=_(u'story'),
        related_name='characters',
    )
    name = models.CharField(
        max_length=200,
        default='',
        blank=False,
        null=False,
        verbose_name=_(u'name')
    )
    order = models.IntegerField(
        default=0,
        blank=False,
        null=False,
        verbose_name=_(u'order'),
        editable=False
    )
    sex = models.SmallIntegerField(
        default=CHAR_SEX_UNDEFINED,
        verbose_name=_(u'sex'),
        choices=CHAR_SEX_CHOICES,
    )

    description = models.TextField(
        verbose_name=_(u'description'),
        blank=True,
        null=True,
    )
    avatar = models.ForeignKey(
        Avatar, models.PROTECT,
        blank=True,
        null=True,
        verbose_name=_(u'avatar'),
        related_name='characters',
    )
    show_in_character_list = models.BooleanField(
        default=False,
        verbose_name=_(u'show in character list')
    )

    def __str__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return 'stories:character', (self.id,), {}

    @models.permalink
    def get_info_url(self):
        return 'stories:character_info', (), {'pk': self.id}


class Variation(SortableModelMixin):
    class Meta:
        verbose_name = _(u'variation')
        verbose_name_plural = _(u'variations')
        ordering = ['order', 'id']

    story = models.ForeignKey(
        Story, models.PROTECT,
        blank=False,
        null=False,
        verbose_name=_(u'story'),
        related_name='variations',
    )
    name = models.CharField(
        max_length=200,
        default='',
        blank=False,
        null=False,
        verbose_name=_(u'name')
    )
    description = models.TextField(
        verbose_name=_(u'description'),
        blank=True,
        null=True,
    )
    game = models.ForeignKey(
        'games.Game', models.PROTECT,
        verbose_name=_(u'game'),
        related_name='story_variation',
        blank=True,
        null=True,
    )

    thread = models.ForeignKey(
        Thread, models.PROTECT,
        verbose_name=_(u'new forum'),
        related_name='variations',
        blank=True,
        null=True,
    )

    comments_count = models.PositiveIntegerField(
        default=0,
        blank=False,
        null=False,
        verbose_name=_(u'comments_count'),
    )

    deleted = models.BooleanField(
        default=False,
        verbose_name=_(u'deleted')
    )

    def __str__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return 'stories:variation', (self.id,), {}

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

    @models.permalink
    def forumlink(self):
        return 'gameforum:variation', (self.pk,), {}

    def get_roles(self):
        return Role.objects.filter(variation=self).exclude(deleted=True)


class Role(SortableModelMixin):
    class Meta:
        verbose_name = _(u'role')
        verbose_name_plural = _(u'roles')
        ordering = ['order', 'id']

    variation = models.ForeignKey(
        Variation, models.PROTECT,
        blank=False,
        null=False,
        verbose_name=_(u'variation'),
        related_name='roles',
    )
    character = models.ForeignKey(
        Character, models.PROTECT,
        blank=True,
        null=True,
        verbose_name=_(u'character'),
        related_name='roles',
    )
    avatar = models.ForeignKey(
        Avatar, models.PROTECT,
        blank=True,
        null=True,
        verbose_name=_(u'avatar'),
        related_name='roles',
    )
    name = models.CharField(
        max_length=200,
        default='',
        blank=False,
        null=False,
        verbose_name=_(u'name')
    )
    sex = models.SmallIntegerField(
        default=CHAR_SEX_UNDEFINED,
        verbose_name=_(u'sex'),
        choices=CHAR_SEX_CHOICES,
    )
    description = models.TextField(
        verbose_name=_(u'description'),
        blank=True,
        null=True,
    )
    body = models.TextField(
        verbose_name=_(u'text'),
        blank=True,
        null=True,
    )
    show_in_character_list = models.BooleanField(
        default=False,
        verbose_name=_(u'show in character list')
    )
    show_in_online_character = models.BooleanField(
        default=True,
        verbose_name=_(u'show in online characters')
    )
    show_trust_marks = models.BooleanField(
        default=True,
        verbose_name=_(u'show trust marks')
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
        verbose_name=_(u'requestable')
    )

    deleted = models.BooleanField(
        default=False,
        blank=False,
        null=False,
        verbose_name=_(u'deleted')
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
        verbose_name=_(u'comments count'),
    )

    trust_value = models.PositiveIntegerField(
        default=0,
        blank=False,
        null=False,
        verbose_name=_(u'trust value'),
    )

    def __str__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return 'stories:role', (self.id,), {}

    @models.permalink
    def get_text_url(self):
        return 'stories:role_text', (self.id,), {}

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


class RoleDeleteMark(models.Model):
    class Meta:
        verbose_name = _(u'role delete mark')
        verbose_name_plural = _(u'roles delete marks')

    role = models.ForeignKey(
        Role, models.PROTECT,
        blank=False,
        null=False,
        verbose_name=_(u'role'),
        related_name='delete_marks',
    )
    user = models.ForeignKey(
        User, models.PROTECT,
        blank=False,
        null=False,
        verbose_name=_(u'user'),
        related_name='role_delete_marks',
    )
    description = models.TextField(
        verbose_name=_(u'description'),
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
        verbose_name = _(u'story admin')
        verbose_name_plural = _(u'story admins')
        unique_together = ('story', 'user')

    CREATE_CHOICES = (
        (False, _('No')),
        (True, _('Yes')),
    )
    story = models.ForeignKey(
        Story, models.PROTECT,
        blank=False,
        null=False,
        verbose_name=_(u'story'),
        related_name='admins',
    )
    user = models.ForeignKey(
        User, models.PROTECT,
        blank=False,
        null=False,
        verbose_name=_(u'user'),
        related_name='admined_stories',
    )
    create_game = models.BooleanField(
        default=False,
        verbose_name=_(u'create game'),
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
        verbose_name = _(u'story author')
        verbose_name_plural = _(u'story authors')
        unique_together = ('story', 'user')

    story = models.ForeignKey(
        Story, models.PROTECT,
        blank=False,
        null=False,
        verbose_name=_(u'story'),
        related_name='authors',
    )
    user = models.ForeignKey(
        User, models.PROTECT,
        blank=False,
        null=False,
        verbose_name=_(u'user'),
        related_name='authored_stories',
    )

    def __str__(self):
        if self.user:
            return str(self.user)
        return None


class AdditionalMaterial(models.Model):
    class Meta:
        verbose_name = _(u'additional material')
        verbose_name_plural = _(u'additional materials')

    story = models.ForeignKey(
        Story, models.PROTECT,
        blank=True,
        null=True,
        verbose_name=_(u'story'),
        related_name='additional_materials',
    )

    variation = models.ForeignKey(
        Variation, models.PROTECT,
        blank=True,
        null=True,
        verbose_name=_(u'variation'),
        related_name='additional_materials',
    )

    name = models.CharField(
        max_length=500,
        unique=False,
        verbose_name=_('name')
    )

    body = models.TextField(
        default='',
        verbose_name=_(u'body')
    )

    admins_only = models.BooleanField(
        default=True,
        verbose_name=_(u'Hide in materials')
    )

    def __str__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        if self.variation and self.variation.game:
            return 'games:edit_material', (self.id,), {}
        return 'stories:edit_material', (self.id,), {}

    @models.permalink
    def url(self):
        if self.variation and self.variation.game:
            return 'games:material', (self.id,), {}
        return 'stories:material', (self.id,), {}

    @models.permalink
    def delete_url(self):
        if self.variation and self.variation.game:
            return 'games:material_delete', (self.id,), {}
        return 'stories:material_delete', (self.id,), {}

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
    story = models.ForeignKey(
        Story, models.PROTECT,
        blank=True,
        null=True,
        verbose_name=_(u'story'),
        related_name='illustrations',
    )

    variation = models.ForeignKey(
        Variation, models.PROTECT,
        blank=True,
        null=True,
        verbose_name=_(u'variation'),
        related_name='illustrations',
    )

    name = models.CharField(
        max_length=500,
        unique=False,
        verbose_name=_('name')
    )

    admins_only = models.BooleanField(
        default=True,
        verbose_name=_(u'Hide in materials')
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
        return self.name

    @models.permalink
    def get_absolute_url(self):
        if self.variation and self.variation.game:
            return 'games:edit_illustration', (self.id,), {}
        return 'stories:edit_illustration', (self.id,), {}

    @models.permalink
    def delete_url(self):
        if self.variation and self.variation.game:
            return 'games:illustration_delete', (self.id,), {}
        return 'stories:illustration_delete', (self.id,), {}

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
        return super(Illustration, self).delete(
            using=using, keep_parents=keep_parents)

    def edit_right(self, user):
        if self.story:
            return self.story.edit_right(user)
        if self.variation:
            return self.variation.edit_right(user)
        return False

    def _copy_file(self, source_path, dest):
        if source_path:
            try:
                source = open(source_path)
                try:
                    dest.save('%s.jpg' % (self.pk,), source)
                finally:
                    source.close()
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
