from django import urls
from django.db import models
from django.utils import html
from django.utils.translation import gettext_lazy as _

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
    )
    edit_role = models.ForeignKey(
        story_models.Role, models.PROTECT,
        null=True,
        blank=True,
        related_name='edited_comments',
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

    def to_json(self, user, detailed=False):
        """ Override original method to avoid resolving "user" foreign key. """
        data = {
            'id': self.pk,
            'thread': {
                'id': self.parent_id,
                # anyway parent is resolved in user
                'url': self.parent.get_absolute_url()
            },
            'page': self.page,
            'user': self.parent.variation.role_to_json(
                self.role_id, user, detailed=detailed),
            'create_time': self.create_time,
        }
        data = {
            **data,
            'url': self.get_absolute_url() if self.pk else None,
            'title': html.escape(self.title),
            'body': bbcodes.bbcode(self.body),
            'edit_right': self.edit_right(user),
            'is_thread': self.is_thread(),
            'edit_time': self.edit_time,
            'editor': self.parent.variation.role_to_json(
                self.edit_role_id, user, detailed=True
            ) if self.edit_time else None,
            'media': self.media,
            'reply_id': self.reply_id,
        }
        signals.to_json.send(
            self.__class__, comment=self, data=data, user=user)
        return data
