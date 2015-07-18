from django.core.urlresolvers import reverse
from djfw.bugtracker.urlizer import BugtrackerUrlizer

class TuliusBugtrackerUrlizer(BugtrackerUrlizer):
    def main_url(self):
        from tulius import urls
        return reverse('bugs:bugs_main', urls, {})
    
    def bug(self, bug_id):
        return reverse( 'bugs:bug', args=(bug_id,))
    
    def bug_by_priority(self, priority_id):
        return reverse( 'bugs:bugs_by_priority', args=(priority_id,))
    
    def bug_by_status(self, status_id):
        return reverse( 'bugs:bugs_by_status', args=(status_id,))
    
    def bug_by_component(self, component_id):
        return reverse( 'bugs:bugs_by_component',  args=(component_id,))
    
    def bug_by_type(self, type_id):
        return reverse( 'bugs:bugs_by_type', args=(type_id,))
    
    def bug_by_version(self, version_id):
        return reverse( 'bugs:bugs_by_version', args=(version_id,))

    def bug_by_version_all(self, version_id):
        return reverse( 'bugs:bugs_by_version_all', args=(version_id,))
    
    def bug_by_version_solved(self, version_id):
        return reverse( 'bugs:bugs_by_version_solved', args=(version_id,))
        
    def bug_by_user(self, jirauser_id):
        return reverse( 'bugs:bugs_by_user', args=(jirauser_id,))
    
    def bug_add_comment(self, bug_id):
        return reverse( 'bugs:issue_add_comment', args=(bug_id,))
    
    def known_bugs(self):
        return reverse( 'bugs:known_bugs', (), {})
    
    def profiler_main(self):
        return reverse( 'bugs:profiler', (), {})
    
    def profiler_by_user(self, module_name, func_name):
        return reverse( 'bugs:profiler_by_user', args=(module_name, func_name,))