from django.utils import timezone

from tulius.forum.threads import signals
from tulius.forum.threads import models
from tulius.websockets import publisher


class Mutation:
    thread = None
    with_descendants = False
    with_parent = False
    with_post_process = False

    def __init__(self, thread, **kwargs):
        self.thread = thread

    def process_thread(self, instance):
        pass

    def post_process(self, instance, children):
        # instance is locked, children are not. They are only for info.
        pass

    def process_parent(self, instance, updated_child):
        pass

    def process_descendant(self, instance, parent):
        # instance should see all changes done on parent
        instance.parent = parent
        self.process_thread(instance)

    def apply(self):
        MutationController(self, self.thread).apply()


class MutationController:
    thread_model: models.Thread = None
    mutations = None
    parent_mutations = None
    instance = None

    def __init__(self, mutation, instance):
        self.thread_model = instance.__class__
        mutations = signals.apply_mutation.send(
            mutation.__class__, instance=instance, mutation=mutation)
        mutations = list(map(lambda x: x[1], mutations))
        # order is important - original mutation applied first.
        self.mutations = [mutation] + [c for c in mutations if c]
        self.parent_mutations = [m for m in self.mutations if m.with_parent]
        self.instance = instance

    def _get_descendants(self, instance):
        return self.thread_model.objects.filter(parent=instance, deleted=False)

    def _apply_descendants(self, instance, mutations):
        post_process = [m for m in mutations if m.with_post_process]
        threads = self._get_descendants(instance)
        processed_threads = []
        for sub_thread in threads:
            sub_thread = self.thread_model.objects.select_for_update().get(
                pk=sub_thread.pk)
            for mutation in mutations:
                mutation.process_descendant(sub_thread, instance)
            if sub_thread.room:
                self._apply_descendants(sub_thread, mutations)
            else:
                for mutation in post_process:
                    mutation.post_process(sub_thread, [])
            sub_thread.save()
            processed_threads.append(sub_thread)
        for mutation in post_process:
            mutation.post_process(instance, processed_threads)

    def _apply_parents(self, instance, parents, mutations):
        post_process = [m for m in mutations if m.with_post_process]
        while parents:
            parent = parents.pop()
            for mutation in mutations:
                mutation.process_parent(parent, instance)
            instance = parent
            if post_process:
                children = instance.children.filter(deleted=False)
                for mutation in post_process:
                    mutation.post_process(instance, children)
            instance.save()

    def apply(self):
        parents = None
        if self.parent_mutations:
            if self.instance.pk:
                parents = list(
                    self.instance.get_ancestors().select_for_update())
            elif self.instance.parent:
                parents = list(
                    self.instance.parent.get_ancestors(
                        include_self=True).select_for_update())
            else:
                parents = []
        for mutation in self.mutations:
            mutation.process_thread(self.instance)
        descendants_mutations = [
            m for m in self.mutations if m.with_descendants]
        if descendants_mutations and self.instance.pk:
            self._apply_descendants(self.instance, descendants_mutations)
        post_process = [m for m in self.mutations if m.with_post_process]
        if post_process:
            children = self.instance.children.filter(deleted=False)
            for mutation in post_process:
                mutation.post_process(self.instance, children)
        self.instance.save()
        if self.parent_mutations and parents:
            self._apply_parents(self.instance, parents, self.parent_mutations)


def on_mutation(mutation, **kwargs):
    def decorator(mutation_class):
        def chain_mutations(instance, **_kwargs):
            return mutation_class(instance, **kwargs)
        signals.apply_mutation.connect(
            chain_mutations, sender=mutation, weak=False)
        return mutation_class
    return decorator


class ThreadDeleteMutation(Mutation):
    with_descendants = True
    user = None
    comment = ''

    def __init__(self, thread, user, comment):
        super(ThreadDeleteMutation, self).__init__(thread)
        self.user = user
        self.comment = comment

    def process_thread(self, instance):
        instance.deleted = True
        instance.data['deleted'] = {
            'user_id': self.user.pk,
            'time': timezone.now().isoformat(),
            'description': self.comment,
        }

    def process_descendant(self, instance, parent):
        # that is a way to detect that thread wasn't deleted itself, but
        # deleted because parent was deleted. It have no record in data.
        instance.deleted = True


class ThreadFixCounters(Mutation):
    result = None
    user = None
    with_descendants = True

    def __init__(self, thread, user=None, result=None):
        super(ThreadFixCounters, self).__init__(thread)
        self.user = user
        self.result = result or {}

    def update_result(self, instance):
        self.result['threads'] = self.result.get('threads', 0) + 1
        if self.user:
            publisher.notify_user_about_fixes(self.user, self.result)

    def process_thread(self, instance):
        instance.__class__.objects.partial_rebuild(instance.tree_id)
        self.update_result(instance)

    def process_descendant(self, instance, parent):
        self.update_result(instance)


class DeletedController(MutationController):
    def _get_descendants(self, instance):
        return self.thread_model.objects.filter(parent=instance)


class RestoreThread(Mutation):
    with_descendants = True

    def process_thread(self, instance):
        instance.deleted = False

    def process_descendant(self, instance, parent):
        if instance.deleted and 'deleted' not in instance.data:
            instance.deleted = False

    def apply(self):
        DeletedController(self, self.thread).apply()
