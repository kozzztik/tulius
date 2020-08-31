from tulius.forum.threads import mutations
from tulius.forum.threads import models
from tulius.forum.comments import signals
from tulius.forum.comments import models as comment_models
from tulius.forum.rights import mutations as right_mutations


class ThreadCommentAdd(mutations.Mutation):
    with_parent = True
    comment = None

    def __init__(self, thread, comment, **kwargs):
        super(ThreadCommentAdd, self).__init__(thread, **kwargs)
        self.comment = comment

    @staticmethod
    def get_last_comment(instance):
        return instance.data.setdefault(
            'last_comment', {'all': None, 'users': {}})

    @staticmethod
    def get_comments_count(instance):
        return instance.data.setdefault(
            'comments_count', {'all': 0, 'users': {}})

    def process_thread(self, instance):
        if 'first_comment_id' not in instance.data:
            instance.data['first_comment_id'] = self.comment.pk
        last_comment = self.get_last_comment(instance)
        last_comment['all'] = self.comment.pk
        comments_count = self.get_comments_count(instance)
        comments_count['all'] += 1

    def process_parent(self, instance, updated_child):
        last_comment = self.get_last_comment(instance)
        comments_count = self.get_comments_count(instance)
        if updated_child.rights(None) & models.ACCESS_READ:
            last_comment['all'] = self.comment.pk
            last_comment['users'] = {
                u: self.comment.pk for u in last_comment['users'].keys()}
            comments_count['all'] += 1
            for u, count in comments_count['users'].items():
                comments_count['users'][u] = count + 1
        else:
            for user, right in self.thread.data['rights']['users'].items():
                if right & models.ACCESS_READ:
                    last_comment['users'][str(user)] = self.comment.pk
                    comments_count['users'][str(user)] = \
                        comments_count['users'].get(str(user), 0) + 1


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
        comments_count = instance.data['comments_count'] = {
            'all': 0, 'users': {}}
        last_comment = instance.data['last_comment'] = {
            'all': None, 'users': {}}
        for c in children:
            if c.rights(None) & models.ACCESS_READ:
                pk = c.data['last_comment']['all']
                if pk and (
                        (not last_comment['all']) or
                        (pk > last_comment['all'])):
                    last_comment['all'] = pk
                if pk:
                    for u, l_pk in last_comment['users'].items():
                        if l_pk < pk:
                            last_comment['users'][u] = pk
                comments_count['all'] += \
                    c.data['comments_count']['all']
                comments_count['all'] += 1
                for u, count in comments_count['users'].items():
                    comments_count['users'][u] = count + 1
            else:
                for user, right in c.data['rights']['users'].items():
                    if right & models.ACCESS_READ:
                        pk = comment_models.get_param(
                            'last_comment', instance, user)
                        new_pk = comment_models.get_param(
                            'last_comment', c, user)
                        if new_pk and ((not pk) or (new_pk > pk)):
                            last_comment['users'][user] = new_pk
                        comments_count['users'][str(user)] = \
                            comment_models.get_param(
                                'comments_count', instance, user) + \
                            comment_models.get_param('comments_count', c, user)

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
        instance.data['comments_count'] = {
            'all': comments_count, 'users': {}}
        instance.data['last_comment'] = {
            'all': last_comment_id, 'users': {}}
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
