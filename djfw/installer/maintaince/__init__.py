import json
import logging
import os
from threading import Thread

from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now
from django.conf import settings


class MaintainceWorker(Thread):

    def __init__(self, log_obj, opts=None):
        from .operations import DEFAULT_OPERATIONS
        self.log_obj = log_obj
        self.logger = logging.getLogger('installer')
        self.bin_dir = 'bin'
        self.bin_path = os.path.join(settings.BASE_DIR, self.bin_dir)
        self.path = settings.BASE_DIR
        from djfw.installer import models, signals
        self.models = models
        self.signals = signals
        self.params = json.loads(log_obj.params) if log_obj.params else {}
        if opts is not None:
            self.params['opts'] = opts
            self.save_params()
        else:
            opts = self.params['opts'] if 'opts' in self.params else []
        self.valid_operations = getattr(
            settings, 'INSTALLER_OPERATIONS', DEFAULT_OPERATIONS)
        self.operations = []
        self.operation = None
        self.resume = log_obj.operation
        found = False
        for operation in self.valid_operations:
            if operation.name in opts:
                if (operation.name == log_obj.operation) or (
                        not log_obj.operation):
                    self.operation = operation(self)
                    self.operations = self.operations + [self.operation]
                    found = True
                elif found:
                    self.operations = self.operations + [operation(self)]
        super(MaintainceWorker, self).__init__()
    
    def save_params(self):
        self.log_obj.params = json.dumps(self.params)
        self.log_obj.save()
        
    def get_form(self, request):
        log_obj = self.log_obj
        if self.operation and (log_obj.state == log_obj.STATE_IN_PROGRESS):
            return self.operation.get_form(request)

    def form_valid(self, form):
        if self.operation:
            self.operation.form_valid(form)
            if self.log_obj.waiting_user:
                self.log_obj.waiting_user = False
                self.log_obj.save()
                self.run()
        
    def update_status(self, status):
        self.log_obj.status = status
        self.log_obj.save()
        self.log(status)
        
    def log(self, text, is_err=False):
        self.models.MaintenanceLogMessage(
            mainteince=self.log_obj, text=text).save()
        if is_err:
            self.logger.error(text)
        else:
            self.logger.warning(text)
        
    def run(self):
        if not self.resume:
            operations = [operation.name for operation in self.operations]
            self.logger.warning(
                "Maintaince started. Options: [%s]" % (','.join(operations)))
            self.signals.maintaince_started.send(self.log_obj, worker=self)
        log_obj = self.log_obj
        try:
            for operation in self.operations:
                self.operation = operation
                log_obj.operation = operation.name
                self.update_status(operation.caption)
                if operation():
                    log_obj.waiting_user = True
                    self.save_params()
                    return
                self.save_params()
            self.signals.maintaince_finished.send(self.log_obj, worker=self)
            log_obj.state = log_obj.STATE_SUCCESS
            log_obj.status = _('Finished')
            log_obj.end_time = now()
            self.save_params()
        except Exception as e:
            log_obj.state = log_obj.STATE_ERROR
            log_obj.status = _('Finished with error')
            log_obj.end_time = now()
            log_obj.save()
            self.save_params()
            self.log('Maintaince finished with error.', True)
            print(e)
            self.log(str(e), True)
