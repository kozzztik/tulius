"""
Forum engine base Thread entity
"""
from django import urls
import django.core.serializers.json
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import html
from django.utils.translation import ugettext_lazy as _

from djfw.wysibb.templatetags import bbcodes
from tulius.forum.threads import signals


User = get_user_model()

NO_ACCESS = 0
ACCESS_READ = 1
ACCESS_WRITE = 2
ACCESS_MODERATE = 4
ACCESS_EDIT = 8
ACCESS_NO_INHERIT = 16

ACCESS_OWN = ACCESS_READ + ACCESS_WRITE + ACCESS_EDIT
ACCESS_OPEN = ACCESS_READ + ACCESS_WRITE
ACCESS_MODERATOR = ACCESS_READ + ACCESS_WRITE + ACCESS_MODERATE

DEFAULT_RIGHTS_CHOICES = (
    (None, _(u'access not set')),
    (ACCESS_READ + ACCESS_WRITE, _(u'free access')),
    (ACCESS_READ, _(u'read only access')),
    (ACCESS_READ + ACCESS_NO_INHERIT, _(u'read only access(no inherit)')),
    (NO_ACCESS, _(u'private(no access)')),
)


DEFAULT = object()


class Counter:
    data = None
    name = None
    instance = None
    default = None

    def __init__(self, instance, name, default=None):
        self.name = name
        self.instance = instance
        self.data = instance.data.get(name)
        self.default = default
        if not self.data:
            self.cleanup()

    def __getitem__(self, item):
        if hasattr(item, 'is_anonymous'):
            if item.is_anonymous:
                return self.data['all']
            if item.is_superuser:
                return self.data['su']
            item = item.pk
        for user in self.data['users']:
            if user['id'] == item:
                return user['value']
        return self.data['all']

    def __setitem__(self, key, value):
        # if hasattr(key, 'pk'):
        #     key = key.pk
        for user in self.data['users']:
            if user['id'] == key:
                user['value'] = value
                return
        self.data['users'].append({'id': key, 'value': value})

    def cleanup(self, default=DEFAULT):
        if default is DEFAULT:
            default = self.default
        self.data = {'all': default, 'su': default, 'users': []}
        self.instance.data[self.name] = self.data

    def __iter__(self):
        for i in self.data['users']:
            yield i['id'], i['value']

    @property
    def users(self):
        result = set()
        for i in self.data['users']:
            result.add(i['id'])
        return result

    @property
    def all(self):
        return self.data['all']

    @all.setter
    def all(self, value):
        self.data['all'] = value

    @property
    def su(self):
        return self.data['su']

    @su.setter
    def su(self, value):
        self.data['su'] = value


class RightsCounter(Counter):
    @property
    def all_inherit(self):
        return self.data.get('all_inherit')

    @all_inherit.setter
    def all_inherit(self, value):
        self.data['all_inherit'] = value


class CounterField:
    name = None
    counter_class = None
    default = None

    def __init__(self, name, counter_class=Counter, default=None):
        self.name = name
        self.counter_class = counter_class
        self.default = default

    def __get__(self, instance, owner):
        return self.counter_class(instance, self.name, default=self.default)


class AbstractThread(models.Model):
    """
    Forum thread
    """
    class Meta:
        verbose_name = _('thread')
        verbose_name_plural = _('threads')
        ordering = ['id']
        abstract = True

    objects = models.Manager()

    title = models.CharField(
        max_length=255,
        unique=False,
        verbose_name=_('title')
    )
    body = models.TextField(verbose_name=_('body'))
    parent = models.ForeignKey(
        'self', models.PROTECT,
        null=True, blank=True,
        related_name='children',
        verbose_name=_('parent thread')
    )
    room = models.BooleanField(
        default=False,
        verbose_name=_(u'room')
    )
    user = models.ForeignKey(
        User, models.PROTECT,
        related_name='%(app_label)s',
        verbose_name=_('author')
    )
    default_rights = models.SmallIntegerField(
        default=None, blank=True, null=True,
        verbose_name=_(u'access type'),
        choices=DEFAULT_RIGHTS_CHOICES,
    )
    create_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('created at'),
    )
    closed = models.BooleanField(
        default=False,
        verbose_name=_(u'closed')
    )
    important = models.BooleanField(
        default=False,
        verbose_name=_(u'important')
    )
    deleted = models.BooleanField(
        default=False,
        verbose_name=_(u'deleted')
    )
    data = models.JSONField(
        default=dict, editable=False,
        encoder=django.core.serializers.json.DjangoJSONEncoder)
    media = models.JSONField(
        default=dict,
        encoder=django.core.serializers.json.DjangoJSONEncoder)
    parents_ids = models.JSONField(
        default=None, blank=True, null=True, editable=False)

    def __str__(self):
        return (self.title or self.body)[:40]

    def get_parents(self, for_update=False):
        if self.parents_ids is None:
            if self.parent:
                self.parents_ids = \
                    self.parent.parents_ids + [self.parent.pk]
            else:
                self.parents_ids = []
        items = self.__class__.objects.filter(pk__in=self.parents_ids)
        if for_update:
            items = items.select_for_update()
        # preserve order
        items = {item.pk: item for item in items}
        return [items[pk] for pk in self.parents_ids]

    def get_children(self, user, deleted=False, **kwargs):
        if (not deleted) and (
                not self.threads_count[user] + self.rooms_count[user]):
            return []
        children = self.children.filter(deleted=deleted, **kwargs)
        return [c for c in children if c.read_right(user)]

    def get_absolute_url(self):
        return urls.reverse('forum_api:thread', kwargs={'pk': self.pk})

    rights = CounterField('rights', counter_class=RightsCounter)
    threads_count = CounterField('threads', default=0)
    rooms_count = CounterField('rooms', default=0)

    def read_right(self, user):
        return bool(
            user.is_superuser or (self.rights[user] & ACCESS_READ))

    def write_right(self, user):
        return bool(
            (not self.closed) and (
                user.is_superuser or (self.rights[user] & ACCESS_WRITE)))

    def moderate_right(self, user):
        return bool(
            user.is_superuser or (self.rights[user] & ACCESS_MODERATE))

    def edit_right(self, user):
        return bool(
            user.is_superuser or (self.rights[user] & ACCESS_EDIT))

    @property
    def moderators(self):
        return User.objects.filter(pk__in=[
            pk for pk, right in self.rights if right & ACCESS_MODERATE])

    @property
    def accessed_users(self):
        if self.default_rights != NO_ACCESS:
            return None
        return User.objects.filter(pk__in=[
            pk for pk, right in self.rights if right & ACCESS_READ])

    def rights_to_json(self, user):
        return {
            'write': self.write_right(user),
            'moderate': self.moderate_right(user),
            'edit': self.edit_right(user),
            'move': self.edit_right(user),
        }

    def to_elastic_search(self, data):
        data['parent_id'] = self.parent_id
        data['user'] = {
            'id': self.user.pk,
            'title': str(self.user)
        }

    @classmethod
    def to_elastic_mapping(cls, fields):
        fields['parents_ids'] = {'type': 'integer'}

    def to_json_as_item(self, user):
        accessed_users = self.accessed_users
        data = {
            'id': self.pk,
            'title': html.escape(self.title),
            'body': bbcodes.bbcode(self.body),
            'room': self.room,
            'deleted': self.deleted,
            'important': self.important,
            'closed': self.closed,
            'user': self.user.to_json(),
            'moderators': [user.to_json() for user in self.moderators],
            'accessed_users': None if accessed_users is None else [
                user.to_json() for user in accessed_users
            ],
            'threads_count': self.threads_count[user],
            'rooms_count': self.rooms_count[user],
            'url': self.get_absolute_url(),
        }
        signals.to_json_as_item.send(
            self.__class__, instance=self, response=data, user=user)
        return data


class Thread(AbstractThread):
    pass


class ThreadCollapseStatus(models.Model):
    """
    Collapsing status saver
    """
    class Meta:
        verbose_name = _('thread access right')
        verbose_name_plural = _('threads access rights')
        unique_together = ('thread', 'user')

    thread = models.ForeignKey(
        Thread, models.PROTECT,
        null=False, blank=False,
        verbose_name=_('thread')
    )
    user = models.ForeignKey(
        User, models.PROTECT,
        null=False, blank=False,
        verbose_name=_('user')
    )
    collapse_threads = models.BooleanField(
        default=False,
        null=False, blank=False,
    )

    collapse_rooms = models.BooleanField(
        default=False,
        null=False, blank=False,
    )
