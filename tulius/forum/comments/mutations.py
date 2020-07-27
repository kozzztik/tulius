from tulius.forum.threads import mutations
from tulius.forum.comments import signals


@mutations.on_mutation(mutations.ThreadDeleteMutation)
class ThreadCommentDelete(mutations.Mutation):
    with_descendants = True

    def process_thread(self, instance):
        if not instance.room:
            signals.on_thread_delete.send(
                instance.__class__, instance=instance, mutation=self)
            instance.comments.update(deleted=True)


def init():
    pass
