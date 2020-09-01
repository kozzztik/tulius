from django.core import exceptions
from django.db import transaction

from tulius.forum import core
from tulius.forum.threads import models
from tulius.forum.threads import mutations


class CountersFix(core.BaseAPIView):
    thread_model = models.Thread
    mutation = mutations.ThreadFixCounters

    @transaction.atomic
    def post(self, request, pk=None, **kwargs):
        if not request.user.is_superuser:
            raise exceptions.PermissionDenied()
        result = {'threads': 0}
        threads = self.thread_model.objects.select_for_update()
        if pk:
            threads = threads.filter(pk=pk)
        else:
            threads = threads.filter(parent=None, deleted=False)
        for thread in threads:
            self.mutation(thread, user=self.user, result=result).apply()
        return {'result': result}
