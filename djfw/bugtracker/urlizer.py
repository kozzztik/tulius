from django.core.urlresolvers import reverse
from django.conf import settings
import importlib

class BugtrackerUrlizer():
    def __init__(self, app='admin'):
        self.app = app
        self.admin = app == 'admin'
    def urls(self):
        return importlib.import_module(settings.ROOT_URLCONF)
    
    def jira_user(self, jira_user):
        return jira_user.user.get_absolute_url() if jira_user.user else None
    
    def bugs_main(self):
        if self.admin:
            return reverse( self.app + ':bugtracker_bug_changelist', self.urls())
        else:
            return reverse( self.app + ':bugtracker_main', self.urls())
            
    def bug(self, bug_id):
        if self.admin:
            return reverse( self.app + ':bugtracker_bug_change', self.urls(), args=(bug_id,))
        else:
            return reverse( self.app + ':bugtracker_bug', self.urls(), args=(bug_id,))
            
    def by_version(self, version_id):
        if self.admin:
            return reverse( self.app + ':bugtracker_bugversion_change', self.urls(), args=(version_id,))
        else:
            return reverse( self.app + ':bugtracker_version', self.urls(), args=(version_id,))
            
    def by_priority(self, priority_id):
        if self.admin:
            return reverse( self.app + ':bugtracker_list', self.urls()) + '?filter=by_priority&id=' + str(priority_id)
        else:
            return reverse( self.app + ':bugtracker_by_priority', self.urls(), args=(priority_id,))
    
    def by_status(self, status_id):
        if self.admin:
            return reverse( self.app + ':bugtracker_list', self.urls()) + '?filter=by_status&id=' + str(status_id)
        else:
            return reverse( self.app + ':bugtracker_by_status', self.urls(), args=(status_id,))
    
    def by_component(self, component_id):
        if self.admin:
            return reverse( self.app + ':bugtracker_list', self.urls()) + '?filter=by_component&id=' + str(component_id)
        else:
            return reverse( self.app + ':bugtracker_by_component', self.urls(), args=(component_id,))
    
    def by_type(self, type_id):
        if self.admin:
            return reverse( self.app + ':bugtracker_list', self.urls()) + '?filter=by_type&id=' + str(type_id)
        else:
            return reverse( self.app + ':bugtracker_by_type', self.urls(), args=(type_id,))
    
    def by_user(self, jirauser_id):
        if self.admin:
            return reverse( self.app + ':bugtracker_list', self.urls()) + '?filter=by_user&id=' + str(jirauser_id)
        else:
            return reverse( self.app + ':bugtracker_by_user', self.urls(), args=(jirauser_id,))
