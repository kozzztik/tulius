from django.db import transaction

from tulius.forum.threads import models
from tulius.forum.threads import mutations


class FooMutation(mutations.Mutation):
    with_parent = True
    with_post_process = True  # to cover default implementation

    def process_parent(self, instance, updated_child):
        instance.body = updated_child.title


def test_mutation_parent_on_not_saved_thread(user):
    parent = models.Thread(title='foo', user=user.user)
    parent.get_parents()  # small hack to fill 'parents' counter
    parent.save()
    thread = models.Thread(title='bar', parent=parent, user=user.user)
    mutation = FooMutation(thread)
    with transaction.atomic():
        mutation.apply()
    parent = models.Thread.objects.get(pk=parent.pk)
    assert parent.body == 'bar'
