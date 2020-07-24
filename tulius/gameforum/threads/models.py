from django.db import models
from django.contrib.auth import get_user_model

from tulius.forum.threads import models as thread_models


User = get_user_model()


class Thread(thread_models.BaseThread):
    role_id = models.IntegerField(blank=True, null=True)
    edit_role_id = models.IntegerField(blank=True, null=True)


class ThreadDeleteMark(thread_models.BaseThreadDeleteMark):
    pass
