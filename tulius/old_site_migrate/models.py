from django.utils.translation import ugettext_lazy as _
from django.db import models
from djfw.news.models import NewsItem
from tulius.games.models import Game, Role, GameAdmin, GameGuest, GameWinner
from tulius.stories.models import Illustration
from tulius.models import User

class OldNews(models.Model):
    """
    Old News
    """
    class Meta:
        verbose_name = _('old news')
        verbose_name_plural = _('old news')
    
    old_id = models.CharField(
        max_length=50, 
        unique=False, 
        verbose_name=_(u'old_id'),
        db_index=True
    )
    
    news_item = models.ForeignKey(
        NewsItem,
        null=True,
        blank=True,
        verbose_name=_(u'news item'),
        related_name='old_versions',
    )
    
    create_time = models.DateTimeField(
        auto_now_add    = True,
        verbose_name    = _('created at'),
    )
    
    title = models.CharField(
        max_length=500, 
        unique=False, 
        verbose_name=_('title')
    )
    
    body = models.TextField(
        default='',
        verbose_name=_(u'text')
    )
    
    def __unicode__(self):
        return self.title
    
class OldUser(models.Model):
    """
    old user record
    """
    class Meta:
        verbose_name = _('old user')
        verbose_name_plural = _('old users')
    
    old_id = models.CharField(
        max_length=50, 
        unique=False, 
        verbose_name=_(u'old_id'),
        db_index=True
    )
    
    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        verbose_name=_(u'user'),
        related_name='old_version',
    )
    
    username = models.CharField(
        max_length=255, 
        unique=False, 
        verbose_name=_('user name')
    )
    
    password = models.CharField(
        max_length=50, 
        unique=False, 
        verbose_name=_('password')
    )

    email = models.CharField(
        max_length=50, 
        unique=False, 
        verbose_name=_('email')
    )
    
    icq = models.CharField(
        max_length=50, 
        unique=False, 
        verbose_name=_('icq')
    )
    
    aol = models.CharField(
        max_length=50, 
        unique=False, 
        verbose_name=_('aol')
    )
    
    msn = models.CharField(
        max_length=50, 
        unique=False, 
        verbose_name=_('msn')
    )
    
    yahoo = models.CharField(
        max_length=50, 
        unique=False, 
        verbose_name=_('yahoo')
    )
    
    website = models.CharField(
        max_length=50, 
        unique=False, 
        verbose_name=_('website')
    )
    
    city = models.CharField(
        max_length=50, 
        unique=False, 
        verbose_name=_('city')
    )
    
    profession = models.CharField(
        max_length=100, 
        unique=False, 
        verbose_name=_('profession')
    )

    hobby = models.CharField(
        max_length=255, 
        unique=False, 
        verbose_name=_('hobby')
    )
    
    subpost = models.TextField(
        verbose_name=_('subpost')
    )
    
    show_email = models.BooleanField(
        verbose_name=_('show email')
    )
    
    hide_on_forum = models.BooleanField(
        verbose_name=_('hide on forum')
    )
    
    show_subpost = models.BooleanField(
        verbose_name=_('show subpost')
    )
    
    html = models.BooleanField(
        verbose_name=_('html')
    )
    
    smiles = models.BooleanField(
        verbose_name=_('smiles')
    )
    
    last_visited = models.PositiveIntegerField(
        verbose_name=_('last visited')
    )
    
    ip = models.CharField(
        max_length=50, 
        unique=False, 
        verbose_name=_('ip')
    )
    
    convert_smiles = models.BooleanField(
        verbose_name=_('convert smiles')
    )
    
    notify_by_email = models.BooleanField(
        verbose_name=_('notify by email')
    )
    
    hide_trust = models.BooleanField(
        verbose_name=_('hide trust')
    )
    
    rank = models.CharField(
        max_length=100, 
        unique=False, 
        verbose_name=_('rank')
    )
    
    def __unicode__(self):
        return self.username
    
class OldGame(models.Model):
    """
    Old game
    """
    class Meta:
        verbose_name = _('old game')
        verbose_name_plural = _('old games')
    
    old_id = models.CharField(
        max_length=50, 
        unique=False, 
        verbose_name=_(u'old_id'),
        db_index=True
    )
    
    game = models.ForeignKey(
        Game,
        null=True,
        blank=True,
        verbose_name=_(u'game'),
        related_name='old_version',
    )
    
    title = models.CharField(
        max_length=500, 
        unique=False, 
        verbose_name=_('title')
    )
    
    comment = models.TextField(
        default='',
        verbose_name=_(u'comment')
    )
    
    status = models.PositiveIntegerField(
        verbose_name=_('status')
    )
    
    introduction = models.TextField(
        default='',
        blank=True,
        verbose_name=_(u'introduction'),
    )
    
    synced = models.BooleanField(
        verbose_name=_('value'),
        default=False
    )
        
    def __unicode__(self):
        return self.title

class OldRole(models.Model):
    """
    Old role
    """
    class Meta:
        verbose_name = _('old role')
        verbose_name_plural = _('old roles')
    
    old_id = models.CharField(
        max_length=50, 
        unique=False, 
        verbose_name=_(u'old_id'),
        db_index=True
    )
    
    game = models.ForeignKey(
        OldGame,
        null=False,
        blank=False,
        verbose_name=_(u'game'),
        related_name='roles',
    )

    user = models.ForeignKey(
        OldUser,
        null=True,
        blank=True,
        verbose_name=_(u'user'),
        related_name='roles',
    )

    role = models.ForeignKey(
        Role,
        null=True,
        blank=True,
        verbose_name=_(u'role'),
        related_name='old_version',
    )
    
    name = models.CharField(
        max_length=500, 
        unique=False, 
        verbose_name=_('name')
    )
    
    comment = models.TextField(
        default='',
        verbose_name=_(u'comment')
    )
    
    requestable = models.BooleanField(
        verbose_name=_('requestable')
    )
    
    show = models.BooleanField(
        verbose_name=_('show')
    )
    
    show_trust = models.BooleanField(
        verbose_name=_('show_trust')
    )

    deleted = models.BooleanField(
        verbose_name=_('deleted')
    )
    
    def __unicode__(self):
        return self.name

class OldGameAdmin(models.Model):
    """
    Old game admin
    """
    class Meta:
        verbose_name = _('old game admin')
        verbose_name_plural = _('old game admins')
    
    old_id = models.CharField(
        max_length=50, 
        unique=False, 
        verbose_name=_(u'old_id'),
        db_index=True
    )
    
    game = models.ForeignKey(
        OldGame,
        null=False,
        blank=False,
        verbose_name=_(u'game'),
        related_name='admins',
    )

    user = models.ForeignKey(
        OldUser,
        null=False,
        blank=False,
        verbose_name=_(u'user'),
        related_name='games_admined',
    )
    
    admin = models.ForeignKey(
        GameAdmin,
        null=True,
        blank=True,
        verbose_name=_(u'admin'),
        related_name='old_version',
    )

class OldGameGuest(models.Model):
    """
    Old game guest
    """
    class Meta:
        verbose_name = _('old game guest')
        verbose_name_plural = _('old game guest')
    
    old_id = models.CharField(
        max_length=50, 
        unique=False, 
        verbose_name=_(u'old_id'),
        db_index=True
    )
    
    game = models.ForeignKey(
        OldGame,
        null=False,
        blank=False,
        verbose_name=_(u'game'),
        related_name='guests',
    )

    user = models.ForeignKey(
        OldUser,
        null=False,
        blank=False,
        verbose_name=_(u'user'),
        related_name='games_guested',
    )
    
    guest = models.ForeignKey(
        GameGuest,
        null=True,
        blank=True,
        verbose_name=_(u'guest'),
        related_name='old_version',
    )

class OldGameWinner(models.Model):
    """
    Old game winner
    """
    class Meta:
        verbose_name = _('old game winner')
        verbose_name_plural = _('old game winner')
    
    old_id = models.CharField(
        max_length=50, 
        unique=False, 
        verbose_name=_(u'old_id'),
        db_index=True
    )
    
    game = models.ForeignKey(
        OldGame,
        null=False,
        blank=False,
        verbose_name=_(u'game'),
        related_name='winners',
    )

    user = models.ForeignKey(
        OldUser,
        null=False,
        blank=False,
        verbose_name=_(u'user'),
        related_name='games_winned',
    )
    
    winner = models.ForeignKey(
        GameWinner,
        null=True,
        blank=True,
        verbose_name=_(u'guest'),
        related_name='old_version',
    )
    
class OldIllustration(models.Model):
    """
    Old Illustration
    """
    class Meta:
        verbose_name = _('old post')
        verbose_name_plural = _('old posts')
    
    old_id = models.CharField(
        max_length=50, 
        unique=False, 
        verbose_name=_(u'old_id'),
        db_index=True
    )
    
    game = models.ForeignKey(
        OldGame,
        null=False,
        blank=False,
        verbose_name=_(u'game'),
        related_name='illustrations',
    )

    illustration = models.ForeignKey(
        Illustration,
        null=True,
        blank=True,
        verbose_name=_(u'illustration'),
        related_name='old_version',
    )

    param1 = models.PositiveIntegerField(
        verbose_name=_('param1')
    )
    
    ext = models.CharField(
        max_length=10, 
        unique=False, 
        verbose_name=_('ext')
    )

    name = models.CharField(
        max_length=255, 
        unique=False, 
        verbose_name=_('name')
    )

    top_banner = models.BooleanField(
        verbose_name=_('top banner')
    )
    
    bottom_banner = models.BooleanField(
        verbose_name=_('bottom banner')
    )
    
    param2 = models.PositiveIntegerField(
        verbose_name=_('param2')
    )
    
    def __unicode__(self):
        return self.name
    
class OldSmile(models.Model):
    """
    Forum smile
    """
    class Meta:
        verbose_name = _('old forum smile')
        verbose_name_plural = _('old forum smiles')
    
    old_id = models.CharField(
        max_length=50, 
        unique=False, 
        verbose_name=_(u'old_id'),
        db_index=True
    )
    
    url = models.CharField(
        max_length=255, 
        unique=False, 
        verbose_name=_('url')
    )
    
    def __unicode__(self):
        return self.old_id
        