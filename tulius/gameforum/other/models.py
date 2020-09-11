from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

from tulius.forum.other import models as other_models
from tulius.gameforum.threads import models as thread_models
from tulius.gameforum.comments import models as comment_models


User = get_user_model()


class ThreadReadMark(other_models.AbstractThreadReadMark):
    thread = models.ForeignKey(
        thread_models.Thread, models.PROTECT,
        null=False, blank=False,
        related_name='read_marks',
        verbose_name=_('thread'),
    )


class CommentLike(other_models.AbstractCommentLike):
    user = models.ForeignKey(
        User, models.PROTECT,
        null=False,
        blank=False,
        related_name='game_liked_comments',
        verbose_name=_('user'),
    )
    comment = models.ForeignKey(
        comment_models.Comment, models.PROTECT,
        null=False,
        blank=False,
        related_name='liked',
        verbose_name=_('comment'),
    )


class VotingVote(other_models.AbstractVotingVote):
    """
    Voting choice
    """
    user = models.ForeignKey(
        User, models.PROTECT,
        null=False,
        blank=False,
        verbose_name=_(u'user'),
        related_name='game_voting_votes',
    )
    comment = models.ForeignKey(
        comment_models.Comment, models.PROTECT,
        null=False,
        blank=False,
        related_name='votes',
        verbose_name=_(u'comment'),
    )
