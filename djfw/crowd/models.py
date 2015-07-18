from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.conf import settings

class User(models.Model):
    username = models.CharField(
        _('username'), 
        max_length=200, 
        unique=True,
    )
    first_name = models.CharField(
        _('first name'), 
        max_length=30, 
        blank=True,
    )
    last_name = models.CharField(
        _('last name'), 
        max_length=30, 
        blank=True,
    )
    display_name = models.CharField(
        _('display name'), 
        max_length=30, 
        blank=True,
    )
    email = models.EmailField(
        _('email address'), 
        blank=True,
    )
    is_active = models.BooleanField(
        _('active'), 
        default=True,
        help_text=_('Designates whether this user should be treated as '
                    'active. Unselect this instead of deleting accounts.')
    )
    is_staff = models.BooleanField(
        _('staff status'), 
        default=False,
        help_text=_('Designates whether the user can log into this admin '
                    'site.')
    )
    is_superuser = models.BooleanField(
        _('superuser status'), 
        default=False,
        help_text=_('Designates that this user has all permissions without '
                    'explicitly assigning them.'))
    token = models.CharField(
        _('token'), 
        max_length=30, 
        blank=True,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        related_name='crowd_user', 
        verbose_name=_('django_user'),
        blank=True,
        null=True,
    )
    groups = models.TextField(
        blank=True,
        null=False,
        default='',
        verbose_name=_(u'groups'),
    )

    def __unicode__(self):
        return self.username
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
