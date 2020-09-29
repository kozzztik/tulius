from tulius.forum.threads import mutations
from tulius.forum.threads import models
from tulius.forum.comments import signals
from tulius.forum.rights import mutations as right_mutations


class ThreadCommentAdd(mutations.Mutation):
    with_parent = True
    comment = None

    def __init__(self, thread, comment, **kwargs):
        super().__init__(thread, **kwargs)
        self.comment = comment

    def process_thread(self, instance):
        users = set()
        if instance.rights.all & models.ACCESS_READ:
            if instance.first_comment.all is None:
                instance.first_comment.all = self.comment.pk
            instance.last_comment.all = self.comment.pk
            instance.comments_count.all += 1
        else:
            users = instance.rights.users
        if instance.first_comment.su is None:
            instance.first_comment.su = self.comment.pk
        instance.last_comment.su = self.comment.pk
        instance.comments_count.su += 1
        for u in users | instance.last_comment.users:
            if instance.rights[u] & models.ACCESS_READ:
                instance.last_comment[u] = self.comment.pk
        for u in users | instance.comments_count.users:
            if instance.rights[u] & models.ACCESS_READ:
                instance.comments_count[u] += 1
        for u in users | instance.first_comment.users:
            if instance.rights[u] & models.ACCESS_READ:
                if instance.first_comment[u] is None:
                    instance.first_comment[u] = self.comment.pk

    def process_parent(self, instance, updated_child):
        if instance.first_comment.su is None:
            instance.first_comment.su = self.comment.pk
        instance.comments_count.su += 1
        instance.last_comment.su = self.comment.pk
        if self.thread.rights.all & models.ACCESS_READ:
            if instance.first_comment.all is None:
                instance.first_comment.all = self.comment.pk
            instance.last_comment.all = self.comment.pk
            for u, _ in instance.last_comment:
                instance.last_comment[u] = self.comment.pk
            instance.comments_count.all += 1
            for u, count in instance.comments_count:
                instance.comments_count[u] = count + 1
        else:
            for user, right in self.thread.rights:
                if right & models.ACCESS_READ:
                    if instance.first_comment[user] is None:
                        instance.first_comment[user] = self.comment.pk
                    instance.last_comment[user] = self.comment.pk
                    instance.comments_count[user] += 1


class FixCounters(mutations.Mutation):
    with_post_process = True
    with_parent = True
    with_comments = True
    with_descendants = True
    result = None

    def __init__(self, thread, result=None, **_kwargs):
        super().__init__(thread)
        self.result = result

    @staticmethod
    def fix_room(instance, children):
        instance.first_comment.cleanup()
        first_comment = instance.first_comment
        instance.comments_count.cleanup()
        comments_count = instance.comments_count
        instance.last_comment.cleanup()
        last_comment = instance.last_comment
        for c in children:
            users = set()
            if not c.rights.all & models.ACCESS_READ:
                users |= c.rights.users
            if c.first_comment.su and (
                    not first_comment.su or
                    first_comment.su > c.first_comment.su):
                first_comment.su = c.first_comment.su
            instance.comments_count.su += c.comments_count.su
            pk = c.last_comment.su
            if pk and (
                    (not last_comment.su) or
                    (pk > last_comment.su)):
                last_comment.su = pk
            if c.rights.all & models.ACCESS_READ:
                pk = c.last_comment.all
                if pk and ((not last_comment.all) or (pk > last_comment.all)):
                    last_comment.all = pk
                pk = c.first_comment.all
                if pk and (
                        (not first_comment.all) or (pk < first_comment.all)):
                    first_comment.all = pk
                child_count = c.comments_count.all
                comments_count.all += child_count
            for u in users | c.comments_count.users | comments_count.users:
                comments_count[u] += c.comments_count[u]
            for u in users | c.first_comment.users | first_comment.users:
                pk = c.first_comment[u]
                if pk and ((not first_comment[u]) or (first_comment[u] > pk)):
                    first_comment[u] = pk
            for u in users | c.last_comment.users | last_comment.users:
                pk = c.last_comment[u]
                if pk and ((not last_comment[u]) or (last_comment[u] < pk)):
                    last_comment[u] = pk

    def fix_comments(self, instance):
        comments = instance.comments.filter(deleted=False)
        comments_count = 0
        first_comment = None
        last_comment = None
        instance.first_comment.all = None
        for comment in comments.order_by('id'):
            comment = instance.comments.select_for_update(
            ).get(pk=comment.pk)
            comment.order = comments_count
            comment.save()
            comments_count += 1
            if not first_comment:
                first_comment = comment.pk
            last_comment = comment.pk
        if self.result:
            self.result['comments'] = \
                self.result.get('comments', 0) + comments_count
        return first_comment, last_comment, comments_count

    def post_process(self, instance, children):
        if instance.deleted:
            return
        if instance.room:
            self.fix_room(instance, children)
            return
        if self.with_comments:
            first_comment, last_comment, count = self.fix_comments(instance)
        else:
            first_comment = instance.first_comment.su
            last_comment = instance.last_comment.su
            count = instance.comments_count.su
        instance.comments_count.cleanup(default=count)
        instance.last_comment.cleanup(default=last_comment)
        instance.first_comment.cleanup(default=first_comment)
        if not instance.rights.all & models.ACCESS_READ:
            instance.comments_count.all = 0
            instance.last_comment.all = None
            instance.first_comment.all = None
            for u, r in instance.rights:
                if r & models.ACCESS_READ:
                    instance.last_comment[u] = last_comment
                    instance.comments_count[u] = count
                    instance.first_comment[u] = first_comment


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
