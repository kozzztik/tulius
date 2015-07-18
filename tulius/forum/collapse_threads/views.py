from tulius.forum.threads.views import BaseThreadView
from django.http import Http404, HttpResponse
import json

class CollapseThreads(BaseThreadView):
    parent_is_room = True
    view_mode = False
    
    def get_context_data(self, **kwargs):
        if self.request.user.is_anonymous():
            raise Http404()
        
        super(CollapseThreads, self).get_context_data(**kwargs)
        ThreadCollapseStatus = self.site.core.models.ThreadCollapseStatus
        try:
            collapse_data =  ThreadCollapseStatus.objects.get(thread=self.parent_thread, user=self.request.user)
        except ThreadCollapseStatus.DoesNotExist:
            collapse_data = ThreadCollapseStatus(thread=self.parent_thread, user=self.request.user)
        if 'threads' in self.request.POST:
            collapse_data.collapse_threads = (self.request.POST['threads'] == '1')
        if 'rooms' in self.request.POST:
            collapse_data.collapse_rooms = (self.request.POST['rooms'] == '1')
        collapse_data.save()
        
    def post(self, request, **kwargs):
        self.get_context_data(**kwargs)
        return HttpResponse(json.dumps({'result': True}))