from tulius.forum.threads import mutations

from tulius.forum.read_marks import models


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


def init():
    pass
