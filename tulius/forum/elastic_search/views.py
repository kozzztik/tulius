from django.core import exceptions

from tulius.forum import core
from tulius.forum.threads import models
from tulius.forum.elastic_search import tasks


class ReindexAll(core.BaseAPIView):
    def post(self, *_args, **_kwargs):
        if not self.user.is_superuser:
            raise exceptions.PermissionDenied()
        result = tasks.reindex_all_entities.apply_async(args=[self.user.pk])
        return {'task_id': result.id}


class ReindexForum(core.BaseAPIView):
    thread_model = models.Thread

    def post(self, *_args, pk=None, **_kwargs):
        if not self.user.is_superuser:
            raise exceptions.PermissionDenied()
        result = tasks.reindex_forum.apply_async(
            args=[
                self.thread_model._meta.app_label,
                self.thread_model._meta.object_name,
                int(pk), self.user.pk])
        return {'task_id': result.id}
