from django import urls
from django.db import models
from django.utils import html
from django.utils.translation import ugettext_lazy as _

from djfw.wysibb.templatetags import bbcodes
from tulius.forum.comments import models as comment_models
from tulius.gameforum.threads import models as thread_models
from tulius.stories import models as story_models
from tulius.forum.comments import signals


class Comment(comment_models.AbstractComment):
    role = models.ForeignKey(
        story_models.Role, models.PROTECT,
        null=True,
        blank=True,
        related_name='comments',
        db_column='role_id'
    )
    edit_role = models.ForeignKey(
        story_models.Role, models.PROTECT,
        null=True,
        blank=True,
        related_name='edited_comments',
        db_column='edit_role_id'
    )
    parent: thread_models.Thread = models.ForeignKey(
        thread_models.Thread, models.PROTECT,
        null=False,
        blank=False,
        related_name='comments',
        verbose_name=_('thread')
    )

    def get_absolute_url(self):
        return urls.reverse(
            'game_forum_api:comment', kwargs={
                'pk': self.pk,
                'variation_id': self.parent.variation_id,
            })

    def to_elastic_search(self, data):
        super().to_elastic_search(data)
        data['variation_id'] = self.parent.variation_id
        data['role_id'] = self.role_id or 0

    @classmethod
    def to_elastic_mapping(cls, fields):
        super().to_elastic_mapping(fields)
        fields['variation_id'] = {'type': 'integer'}

    def to_json(self, user):
        """ Override original method to avoid resolving "user" foreign key. """
        data = {
            'id': self.pk,
            'thread': {
                'id': self.parent_id,
                'url': self.parent.get_absolute_url()
            },
            'page': self.order_to_page(self.order),
            'url': self.get_absolute_url() if self.pk else None,
            'title': html.escape(self.title),
            'body': bbcodes.bbcode(self.body),
            'user':
                self.role.to_json(user, detailed=True)
                if self.role else story_models.leader_json(),
            'create_time': self.create_time,
            'edit_right': self.edit_right(user),
            'is_thread': self.is_thread(),
            'edit_time': self.edit_time,
            'editor': None,
            'media': self.media,
            'reply_id': self.reply_id,
        }
        if self.edit_time:
            data['editor'] = \
                self.edit_role.to_json(user, detailed=True) \
                if self.edit_role else story_models.leader_json()
        signals.to_json.send(
            self.__class__, comment=self, data=data, user=user)
        return data
