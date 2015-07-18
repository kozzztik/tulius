from tulius.forum.plugins import BasePluginView
from tulius.stories.models import Role
from django.http import HttpResponse
import json

class DoTrustmark(BasePluginView):
    def get(self, request, **kwargs):
        models = self.site.gamemodels
        target_id =int( request.GET['target_id'])
        value = int(request.GET['value'])
        role = Role.objects.get(id=target_id)
        if role.user == request.user:
            raise Exception(_('You can`t vote for yourself!'))
        if not role.variation.game:
            raise Exception(_('You can`t vote for characters in variation!'))
        if not role.variation.game.write_right(request.user):
            raise Exception(_('You can`t vote in this game!'))
        trustmarks = models.Trustmark.objects.filter(user=request.user, role=role)
        if trustmarks:
            trustmark = trustmarks[0]
        else:
            trustmark = models.Trustmark(user=request.user, role=role, variation=role.variation)
        trustmark.value = value
        trustmark.save()
        all_marks = self.site.core.recalc_role_trust(role)
        my_mark = self.site.core.mark_to_percents(value)
        ret_json = {'success': True, 'my_mark': my_mark, 'all_marks': all_marks}
        return HttpResponse( json.dumps( ret_json ) )