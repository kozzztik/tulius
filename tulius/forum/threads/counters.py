from django.core import exceptions
from django.db import transaction

from tulius.forum import plugins
from tulius.forum import models
from tulius.forum.threads import signals
from tulius.websockets import publisher


class CountersFix(plugins.BaseAPIView):
    thread_model = models.Thread
    result = None
    notify_user = True
    plugin_id = None

    def process_thread(self, thread, with_descendants):
        thread_calls = signals.on_fix_counters.send(
            self.thread_model, thread=thread,
            with_descendants=with_descendants, view=self)
        thread_calls = list(map(lambda x: x[1], thread_calls))
        if with_descendants and thread.room:
            threads = self.thread_model.objects.filter(
                parent=thread, deleted=False)
            for sub_thread in threads:
                sub_thread = self.thread_model.objects.select_for_update().get(
                    pk=sub_thread.pk)
                sub_result = self.process_thread(
                    sub_thread, with_descendants)
                thread_calls += sub_result
        parent_results = []
        thread_calls = [c for c in thread_calls if c]
        for thread_call in thread_calls:
            sub_result = thread_call(thread)
            if sub_result:
                parent_results.append(sub_result)
        thread.save()
        self.result['threads'] = self.result.get('threads', 0) + 1
        if self.notify_user:
            publisher.notify_user_about_fixes(self.user, self.result)
        return parent_results

    @transaction.atomic
    def post(self, request, pk=None, **kwargs):
        if not request.user.is_superuser:
            raise exceptions.PermissionDenied()
        self.result = {}
        threads = self.thread_model.objects.select_for_update()
        if pk:
            threads = threads.filter(pk=pk, plugin_id=self.plugin_id)
        else:
            threads = threads.filter(
                parent=None, deleted=False, plugin_id=self.plugin_id)
        for thread in threads:
            self.process_thread(thread, True)
        return {'result': self.result}
