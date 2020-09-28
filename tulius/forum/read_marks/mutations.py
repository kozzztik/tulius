from django import dispatch

from tulius.forum.threads import mutations
from tulius.forum.threads import signals
from tulius.forum.rights import mutations as rights_mutations
from tulius.forum.read_marks import models
from tulius.forum.read_marks import tasks


@mutations.on_mutation(mutations.ThreadCreateMutation)
class OnAddThread(mutations.Mutation):
    read_mark_model = models.ThreadReadMark
    with_parent = True

    def process_thread(self, instance):
        # thread is not saved yet, do on process parent, as threads always
        # have parents
        pass

    def process_parent(self, instance, updated_child):
        if (not self.thread.room) and (updated_child.pk == self.thread.pk):
            self.read_mark_model(
                user=self.thread.user, thread=self.thread,
                not_read_comment_id=None
            ).save()
        self.read_mark_model.objects.get_or_create(
            user=self.thread.user, thread=self.thread,
            defaults={
                'not_read_comment_id':
                    instance.first_comment[self.thread.user]})


@mutations.on_mutation(mutations.RestoreThread)
@mutations.on_mutation(rights_mutations.UpdateRights)
@mutations.on_mutation(mutations.ThreadDeleteMutation)
class OnThreadChange(mutations.Mutation):
    with_parent = True

    def process_parent(self, instance, updated_child):
        # start task on parents processing - original thread is updated in DB.
        # task is started only for direct parent of original thread
        if updated_child.pk == self.thread.pk:
            tasks.update_read_marks_on_rights_async(instance)


@dispatch.receiver(signals.after_move)
def on_thread_move(instance, old_parent, **_kwargs):
    tasks.update_read_marks_on_rights_async(old_parent)
    tasks.after_thread_move_async(instance)


def init():
    pass
