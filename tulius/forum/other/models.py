import typing

from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
import jsonfield

from tulius.forum.threads import models as thread_models
from tulius.forum.comments import models as comment_models

User = get_user_model()


class AbstractThreadReadMark(models.Model):
    """
    Mark on thread, what last post was read
    """
    class Meta:
        verbose_name = _('thread read mark')
        verbose_name_plural = _('thread read marks')
        abstract = True

    user = models.ForeignKey(
        User, models.PROTECT,
        null=False, blank=False,
        related_name='%(app_label)s_readed_threads',
        verbose_name=_('user'),
    )
    readed_comment_id = models.IntegerField(null=False, blank=False)
    not_readed_comment_id = models.IntegerField(
        null=True, blank=True,
        db_index=True)


class ThreadReadMark(AbstractThreadReadMark):
    thread = models.ForeignKey(
        thread_models.Thread, models.PROTECT,
        null=False, blank=False,
        related_name='read_marks',
        verbose_name=_('thread'),
    )


def default_json():
    return {}


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
    data: typing.Dict = jsonfield.JSONField(default=default_json)


class CommentLike(AbstractCommentLike):
    pass


class AbstractOnlineUser(models.Model):
    class Meta:
        verbose_name = _(u'online user')
        verbose_name_plural = _(u'online users')
        unique_together = ['user', 'thread']
        abstract = True

    user = models.ForeignKey(
        User, models.PROTECT,
        blank=False,
        null=False,
        verbose_name=_(u'user'),
        related_name='forum_visit',
    )
    visit_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('visit time'),
    )
    thread = models.ForeignKey(
        thread_models.Thread, models.PROTECT,
        blank=False,
        null=False,
        verbose_name=_(u'thread'),
        related_name='visit_marks',
    )

    def __str__(self):
        return str(self.user)


class OnlineUser(AbstractOnlineUser):
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
