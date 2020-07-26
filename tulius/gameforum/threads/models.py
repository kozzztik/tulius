from django.db import models
from django.contrib.auth import get_user_model

from tulius.forum.threads import models as thread_models


User = get_user_model()


class Thread(thread_models.AbstractThread):
    role_id = models.IntegerField(blank=True, null=True)
    edit_role_id = models.IntegerField(blank=True, null=True)
    variation_id = models.IntegerField(blank=False, null=False)
