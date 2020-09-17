from django.db import models
from django.contrib.auth import get_user_model

from tulius.forum.threads import models as thread_models


User = get_user_model()


class AbstractThreadReadMark(models.Model):
    """
    Mark on thread, what last post was read
    """
    class Meta:
        abstract = True

    objects = models.Manager()  # linter, be happy

    user = models.ForeignKey(
        User, models.PROTECT,
        null=False, blank=False,
        related_name='%(app_label)s_read_marks',
    )
    not_read_comment_id = models.IntegerField(
        null=True, blank=True,
        db_index=True)
    thread = models.ForeignKey(
        thread_models.Thread, models.PROTECT,
        null=False, blank=False,
        related_name='read_marks_old',
    )


class ThreadReadMark(AbstractThreadReadMark):
    pass
