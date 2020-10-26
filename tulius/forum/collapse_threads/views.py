import json

from tulius.forum import core
from tulius.forum.threads import models


class CollapseAPIList(core.BaseAPIView):
    require_user = True

    def get_context_data(self, **kwargs):
        super().get_context_data(**kwargs)
        objs = models.ThreadCollapseStatus.objects.filter(user=self.user)
        return {
            obj.thread_id: obj.collapse_rooms for obj in objs
        }


class CollapseAPISave(core.BaseAPIView):
    require_user = True

    def post(self, request, **kwargs):
        pk = self.kwargs.get('pk')
        obj, _ = models.ThreadCollapseStatus.objects.get_or_create(
            thread_id=pk, user=self.user
        )
        data = json.loads(self.request.body)
        obj.collapse_rooms = bool(data['value'])
        obj.save()
        return {'id': pk, 'value': obj.collapse_rooms}
