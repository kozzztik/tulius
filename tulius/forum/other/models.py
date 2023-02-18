import typing

import django.core.serializers.json
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from tulius.forum.comments import models as comment_models

User = get_user_model()


class AbstractCommentLike(models.Model):
    class Meta:
        verbose_name = _('comment like')
        verbose_name_plural = _('comments likes')
        abstract = True

    objects = models.Manager()  # linter, be happy

    user = models.ForeignKey(
        User, models.PROTECT,
        null=False,
        blank=False,
        related_name='liked_comments',
        verbose_name=_('user'),
    )
    comment = models.ForeignKey(
        comment_models.Comment, models.PROTECT,
        null=False,
        blank=False,
        related_name='liked',
        verbose_name=_('comment'),
    )
    data: typing.Dict = models.JSONField(
        default=dict,
        encoder=django.core.serializers.json.DjangoJSONEncoder)


class CommentLike(AbstractCommentLike):
    pass


class AbstractVotingVote(models.Model):
    """
    Voting choice
    """
    class Meta:
        verbose_name = _('voting vote')
        verbose_name_plural = _('voting votes')
        unique_together = ('user', 'comment')
        abstract = True

    choice = models.IntegerField(
        blank=False,
        null=False,
        verbose_name=_('choice')
    )
    user = models.ForeignKey(
        User, models.PROTECT,
        null=False,
        blank=False,
        verbose_name=_(u'user'),
        related_name='voting_votes',
    )
    comment = models.ForeignKey(
        comment_models.Comment, models.PROTECT,
        null=False,
        blank=False,
        related_name='votes',
        verbose_name=_(u'comment'),
    )

    def __str__(self):
        return f'{self.comment.title} - {self.choice}({self.user})'


class VotingVote(AbstractVotingVote):
    pass
