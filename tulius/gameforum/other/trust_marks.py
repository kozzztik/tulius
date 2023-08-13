import json

from django import shortcuts
from django.core import exceptions

from tulius.gameforum import models
from tulius.gameforum import base
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
        marksum = marksum / markcount
    value = mark_to_percents(marksum)
    value = min(value, 100)
    value = max(value, 0)
    role.trust_value = value
    role.save()
    return value


class TrustMarkAPI(base.VariationMixin):
    def post(self, request, role_id=None, **kwargs):
        role = shortcuts.get_object_or_404(
            stories_models.Role, id=int(role_id), variation=self.variation)
        value = int(json.loads(request.body)['value'])
        if role.user == self.user:
            raise exceptions.PermissionDenied('Can`t vote for yourself!')
        if not role.variation.game:
            raise exceptions.PermissionDenied(
                'Can`t vote for characters in variation')
        if not self.variation.game.write_right(request.user):
            raise exceptions.PermissionDenied('Сan`t vote in this game')
        trust_mark = models.Trustmark.objects.get_or_create(
            user=self.user, role=role, variation=role.variation,
            defaults={'value': value})[0]
        trust_mark.value = value
        trust_mark.save()
        all_marks = recalc_role_trust(role)
        my_mark = mark_to_percents(value)
        return {
            'my_trust': my_mark,
            'trust_value': all_marks
        }
