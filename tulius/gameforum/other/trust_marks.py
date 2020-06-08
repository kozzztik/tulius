from django import shortcuts
from django.core import exceptions

from tulius.gameforum import models
from tulius.gameforum import views
from tulius.stories import models as stories_models

max_val = 3


def mark_to_percents(mark_value):
    return int(50 + (mark_value * 50 / max_val))


def recalc_role_trust(role):
    trustmarks = models.Trustmark.objects.filter(role=role)
    markcount = len(trustmarks)
    marksum = 0
    for mark in trustmarks:
        marksum += mark.value
    if markcount:
        marksum = (marksum / markcount)
    value = mark_to_percents(marksum)
    if value > 100:
        value = 100
    if value < 0:
        value = 0
    role.trust_value = value
    role.save()
    return value


class TrustMarkAPI(views.VariationMixin):
    def post(self, request, *args, role_id=None):
        role = shortcuts.get_object_or_404(
            stories_models.Role, id=int(role_id), variation=self.variation)
        value = int(request.POST['value'])
        if role.user == self.user:
            raise exceptions.PermissionDenied('Can`t vote for yourself!')
        if not role.variation.game:
            raise exceptions.PermissionDenied(
                'Can`t vote for characters in variation')
        if not self.variation.game.write_right(request.user):
            raise exceptions.PermissionDenied('Сan`t vote in this game')
        trust_mark = models.Trustmark.objects.get_or_create(
            user=self.user, role=role, variation=role.variation)[1]
        trust_mark.value = value
        trust_mark.save()
        all_marks = recalc_role_trust(role)
        my_mark = mark_to_percents(value)
        return {
            'my_mark': my_mark,
            'all_marks': all_marks
        }
