from django.conf import settings
from django.core.urlresolvers import reverse
from .views import on_maintaince_view
from .models import get_lock_file_name, MaintenanceLog
import os

class MaintenanceMiddleware(object):
    def __init__(self):
        self.lock_file_name = get_lock_file_name()
        self.lock_view = getattr(settings, 'INSTALLER_LOCK_VIEW', None)
        if not self.lock_view:
            self.lock_view = on_maintaince_view
        
    def process_request(self, request):
        if not os.path.exists(self.lock_file_name):
            return None
        if request.path == reverse('admin:index'):
            return None
        if request.path.find(reverse('admin:app_list', kwargs={'app_label': 'installer'})) >= 0 :
            return None
        obj = None
        try:
            f = open(self.lock_file_name, 'r')
            try:
                old_id = int(f.read())
                obj = MaintenanceLog.objects.get(id=old_id)
            finally:
                f.close()
        except:
            pass
        return self.lock_view(request, obj)