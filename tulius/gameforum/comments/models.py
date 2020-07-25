from django.db import models
from django.utils.translation import ugettext_lazy as _
from mptt import models as mptt_models

from tulius.forum.comments import models as comment_models
from tulius.gameforum.threads import models as thread_models


class Comment(comment_models.AbstractComment):
    role_id = models.IntegerField(blank=True, null=True)
    edit_role_id = models.IntegerField(blank=True, null=True)
    parent = mptt_models.TreeForeignKey(
        thread_models.Thread, models.PROTECT,
        null=False,
        blank=False,
        related_name='comments',
        verbose_name=_('thread')
    )
