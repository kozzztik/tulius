from django import urls
from django.db import models
from django.utils.translation import ugettext_lazy as _

from tulius.forum.comments import models as comment_models
from tulius.gameforum.threads import models as thread_models


class Comment(comment_models.AbstractComment):
    role_id = models.IntegerField(blank=True, null=True, db_index=True)
    edit_role_id = models.IntegerField(blank=True, null=True)
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
