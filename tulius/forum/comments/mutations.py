from tulius.forum.threads import mutations
from tulius.forum.threads import models
from tulius.forum.comments import signals
from tulius.forum.rights import mutations as right_mutations


class ThreadCommentAdd(mutations.Mutation):
    with_parent = True
    comment = None

    def __init__(self, thread, comment, **kwargs):
        super(ThreadCommentAdd, self).__init__(thread, **kwargs)
        self.comment = comment

    def process_thread(self, instance):
        if 'first_comment_id' not in instance.data:
            instance.data['first_comment_id'] = self.comment.pk
        instance.last_comment.all = self.comment.pk
        instance.last_comment.su = self.comment.pk
        instance.comments_count.all += 1
        instance.comments_count.su += 1

    def process_parent(self, instance, updated_child):
        instance.comments_count.su += 1
        instance.last_comment.su = self.comment.pk
        if updated_child.rights.all & models.ACCESS_READ:
            instance.last_comment.all = self.comment.pk
            for u, _ in instance.last_comment:
                instance.last_comment[u] = self.comment.pk
            instance.comments_count.all += 1
            for u, count in instance.comments_count:
                instance.comments_count[u] = count + 1
        else:
            for user, right in self.thread.rights:
                if right & models.ACCESS_READ:
                    instance.last_comment[user] = self.comment.pk
                    instance.comments_count[user] += 1


class FixCounters(mutations.Mutation):
    with_post_process = True
    with_parent = True
    with_comments = True
    with_descendants = True
    result = None

    def __init__(self, thread, result=None):
        super(FixCounters, self).__init__(thread)
        self.result = result

    @staticmethod
    def fix_room(instance, children):
        instance.comments_count.cleanup()
        comments_count = instance.comments_count
        instance.last_comment.cleanup()
        last_comment = instance.last_comment
        for c in children:
            instance.comments_count.su += c.comments_count.su
            pk = c.last_comment.su
            if pk and (
                    (not last_comment.su) or
                    (pk > last_comment.su)):
                last_comment.su = pk
            if c.rights.all & models.ACCESS_READ:
                pk = c.last_comment.all
                if pk and (
                        (not last_comment.all) or
                        (pk > last_comment.all)):
                    last_comment.all = pk
                if pk:
                    for u, l_pk in last_comment:
                        if l_pk < pk:
                            last_comment[u] = pk
                child_count = c.comments_count.all
                comments_count.all += child_count
                for u, count in comments_count:
                    comments_count[u] = count + child_count
            else:
                for user, right in c.rights:
                    if right & models.ACCESS_READ:
                        pk = last_comment[user]
                        new_pk = c.last_comment[user]
                        if new_pk and ((not pk) or (new_pk > pk)):
                            last_comment[user] = new_pk
                        comments_count[user] += c.comments_count[user]

    def post_process(self, instance, children):
        if instance.deleted:
            return
        if instance.room:
            self.fix_room(instance, children)
            return
        if not self.with_comments:
            return
        comments = instance.comments.filter(deleted=False)
        comments_count = 0
        last_comment_id = None
        instance.data['first_comment_id'] = None
        for comment in comments.order_by('id'):
            comment = instance.comments.select_for_update(
                ).get(pk=comment.pk)
            comment.order = comments_count
            comment.save()
            comments_count += 1
            if not instance.data['first_comment_id']:
                instance.data['first_comment_id'] = comment.pk
            last_comment_id = comment.pk
        instance.comments_count.cleanup(default=comments_count)
        instance.last_comment.cleanup(default=last_comment_id)
        if self.result:
            self.result['comments'] = \
                self.result.get('comments', 0) + comments_count


def on_fix_mutation(mutation, instance, **_kwargs):
    return FixCounters(instance, result=mutation.result)


mutations.signals.apply_mutation.connect(
    on_fix_mutation, sender=mutations.ThreadFixCounters)


@mutations.on_mutation(right_mutations.UpdateRights)
class FixCountersOnRights(FixCounters):
    with_comments = False


@mutations.on_mutation(mutations.ThreadDeleteMutation)
class ThreadCommentDelete(FixCounters):
    with_descendants = True

    def process_thread(self, instance):
        if not instance.room:
            signals.on_thread_delete.send(
                instance.__class__, instance=instance, mutation=self)
            instance.comments.update(deleted=True)


@mutations.on_mutation(mutations.RestoreThread)
class ThreadRestore(mutations.Mutation):
    with_descendants = True

    def process_thread(self, instance):
        if not instance.room:
            for comment in instance.comments.filter(deleted=True):
                if 'deleted' not in comment.data:
                    instance.comments.filter(pk=comment.pk).update(
                        deleted=False)


def init():
    pass
