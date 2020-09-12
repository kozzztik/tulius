from tulius.stories import models as stories_models
from tulius.forum.threads import mutations
from tulius.forum.comments import mutations as comments_mutatuions
from tulius.gameforum.comments import models as comment_models


class ThreadCreateMutation(mutations.ThreadCreateMutation):
    variation = None

    def __init__(self, thread, data, view, **kwargs):
        self.variation = view.variation
        super(ThreadCreateMutation, self).__init__(thread, data, **kwargs)


class ThreadFixCounters(mutations.ThreadFixCounters):
    def fix_variation(self, instance):
        if instance.parent_id or not instance.pk:
            return None
        variation = stories_models.Variation.objects.select_for_update(
            ).get(thread=instance)
        roles = stories_models.Role.objects.filter(variation=variation)
        for role in roles:
            role = stories_models.Role.objects.select_for_update(
                ).get(pk=role.pk)
            role.comments_count = comment_models.Comment.objects.filter(
                parent__parents_ids__contains=instance.pk, deleted=False,
                role_id=role.id).count()
            role.save()
        variation.comments_count = comment_models.Comment.objects.filter(
            parent__parents_ids__contains=instance.pk, deleted=False).count()
        variation.save()
        return None

    def process_thread(self, instance):
        self.fix_variation(instance)
        super(ThreadFixCounters, self).process_thread(instance)


mutations.signals.apply_mutation.connect(
    comments_mutatuions.on_fix_mutation, sender=ThreadFixCounters)

on_mutation = mutations.on_mutation
