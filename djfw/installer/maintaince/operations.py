from django.utils.translation import ugettext_lazy as _
from repository import RepoUpdate
from django.conf import settings
from .backup import do_backup
import os
from .operation import Operation

        
class BackupOperation(Operation):
    name = 'backup'
    caption = _(u'Do backup')
    
    def __call__(self):
        do_backup('maintaince')
        

apache_conf_addition = """import os
os.environ['DJANGO_SETTINGS_MODULE'] = '$PROJECT_NAME.settings'
os.environ['PYTHON_EGG_CACHE'] = '$PROJECTDIRtmp-eggs'

import django.core.handlers.wsgi

_application = django.core.handlers.wsgi.WSGIHandler()

def application(environ, start_response):
    environ['PATH_INFO'] = environ['SCRIPT_NAME'] + environ['PATH_INFO']
    return _application(environ, start_response)
"""
repl_str = """import djangorecipe.manage
import os
os.environ['DJANGO_SETTINGS_MODULE'] = '$PROJECT_NAME.settings'
os.environ['PYTHON_EGG_CACHE'] = '$PROJECTDIRtmp-eggs'
"""

class Buildout(Operation):
    name = 'buildout'
    caption = _(u'Update dependecies')
    
    def __call__(self):
        bin_path = self.worker.bin_path
        buildout_name = os.path.join(self.path, 'buildout.cfg')
        logs = self.models.MaintenanceLog.objects.filter(buildout_update_time__isnull=False).order_by('-id')
        buildout_update_time = logs[0].buildout_update_time if logs else None
        if os.path.exists(buildout_name):
            new_buildout_update_time = os.path.getmtime(buildout_name)
            if (not buildout_update_time) or (new_buildout_update_time > buildout_update_time):
                self.worker.update_status(_("Downloading dependencies"))
                self.subprocess(os.path.join(bin_path, 'buildout'))
                self.log_obj.buildout_update_time = new_buildout_update_time
                self.log_obj.save()
        django_conf_name = 'django-script.py'
        if not os.path.exists(os.path.join(bin_path, django_conf_name)):
            django_conf_name = 'django'
            
        django_conf = self.read_file(django_conf_name, bin_path)
        apache_conf = django_conf
        if django_conf.find('PYTHON_EGG_CACHE') < 0:
            my_repl_str = repl_str.replace('$PROJECT_NAME', settings.PROJECT_NAME).replace('$PROJECT_NAME', self.path)
            django_conf = django_conf.replace('import djangorecipe.manage', my_repl_str)
            self.write_file(django_conf_name, django_conf, bin_path)
        pos = apache_conf.find('import djangorecipe')
        if pos >= 0:
            apache_conf = apache_conf[:pos]
        self.write_file('env.py', apache_conf, bin_path)
        apache_conf += apache_conf_addition
        apache_conf = apache_conf.replace('$PROJECT_NAME', settings.PROJECT_NAME).replace('$PROJECT_NAME', self.path)
        self.write_file('apache.py', apache_conf, bin_path)
        
class UpdateVhost(Operation):
    name = 'vhost'
    caption = _(u'Update apache virtual host')
    
    def __call__(self):
        vhost_cfg = self.read_file('vhost.conf.template')
        self.write_file('vhost.conf', vhost_cfg.replace('%PWD%', self.path))
        
class SyncDB(Operation):
    name = 'syncdb'
    caption = _(u'Migrate DB')
    
    def __call__(self):
        self.subprocess(os.path.join(self.worker.bin_path, 'django') + ' syncdb')
        self.subprocess(os.path.join(self.worker.bin_path, 'django') + ' migrate')
        
class CollectStatic(Operation):
    name = 'collectstatic'
    caption = _(u'Collect static files')
    
    def __call__(self):
        self.subprocess(os.path.join(self.worker.bin_path, 'django') + ' collectstatic --noinput')

class ApacheRestart(Operation):
    name = 'apache_restart'
    caption = _(u'Restart apache')
    
    def __call__(self):
        from django.conf import settings
        if settings.DEBUG:
            self.worker.log('DEBUG mode, no need to restart apache')
        else:
            import platform
            is_windows = platform.system() == 'Windows'
            if is_windows:
                self.worker.log('No apache restart on windows')
            else:
                self.worker.log('Restarting apache')
                self.subprocess('sudo /etc/init.d/apache2 reload')

DEFAULT_OPERATIONS = [
    BackupOperation, 
    RepoUpdate, 
    Buildout, 
    UpdateVhost, 
    SyncDB,
    CollectStatic,
    ApacheRestart
]