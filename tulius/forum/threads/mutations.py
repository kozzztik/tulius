from django.utils import timezone

from tulius.forum.threads import signals
from tulius.forum.threads import models


class Mutation:
    thread = None
    with_descendants = False
    with_parent = False

    def __init__(self, thread):
        self.thread = thread

    def process_thread(self, instance):
        pass

    def process_parent(self, instance, updated_child):
        pass

    def process_descendant(self, instance, parent):
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
            mutation.__class__, instance=instance, mutation=self)
        mutations = list(map(lambda x: x[1], mutations))
        # order is important - original mutation applied first.
        self.mutations = [mutation] + [c for c in mutations if c]
        self.parent_mutations = [m for m in mutations if m.with_parent]
        self.instance = instance

    def _apply_descendants(self, instance, mutations):
        threads = self.thread_model.objects.filter(
            parent=instance, deleted=False)
        for sub_thread in threads:
            sub_thread = self.thread_model.objects.select_for_update().get(
                pk=sub_thread.pk)
            for mutation in mutations:
                mutation.process_descendant(sub_thread, instance)
            if sub_thread.room:
                self._apply_descendants(sub_thread, mutations)
            sub_thread.save()

    def _apply_parents(self, instance, parents, mutations):
        while parents:
            parent = parents.pop()  # TODO check ordering
            for mutation in mutations:
                mutation.process_parent(parent, instance)
            parent.save()
            instance = parent

    def apply(self):
        parents = None
        if self.parent_mutations:
            parents = list(self.instance.get_ancestors().select_for_update())
        for mutation in self.mutations:
            mutation.process_thread(self.instance)
        descendants_mutations = [
            m for m in self.mutations if m.with_descendants]
        if descendants_mutations:
            self._apply_descendants(self.instance, descendants_mutations)
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
