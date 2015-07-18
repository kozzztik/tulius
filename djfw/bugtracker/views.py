from django.template import loader, RequestContext
from django.http import HttpResponse, Http404
from django.conf.urls import patterns, url
from .forms import FoundBugForm, FoundbugUploadForm
import json
from .admin_views import BugsView, BugsByPriorityView, BugsByStatusView, BugsByComponentView,\
    BugsByTypeView, BugsByUserView, BugView, VersionsView, VersionView
from .core import *
from .urlizer import BugtrackerUrlizer

def known_bugs():
    version_id = get_setting( DEFAULT_VERSION_KEY)
    if not version_id:
        return None
    version = BugVersion.objects.get(id=version_id)
    return version.bugs.filter(bug__resolution_time__isnull = True).order_by('bug__priority', '-bug__create_time')
    
def view_sync_all(request):
    if not request.user.is_superuser:
        raise Http404()
    do_sync_all()
    return HttpResponse( json.dumps({'success': True}) )

def found_bug(request, exception_id=None, template_name='bugtracker/add_bug_form.haml' ):
    version_id = get_setting(DEFAULT_VERSION_KEY)
    priority_id = get_setting(DEFAULT_PRIORITY_KEY)
    type_id = get_setting(DEFAULT_BUG_TYPE_KEY)
    status_id = get_setting(DEFAULT_BUG_STATUS_KEY)
    if exception_id:
        exception_id = int(exception_id)
        try:
            from djfw.logger.models import ExceptionMessage
        except ImportError:
            from logger.models import ExceptionMessage
        return ExceptionMessage.objects.get(id=exception_id)
        exception = ExceptionMessage.objects.get(id = exception_id)
    else:
        exception = None 
    response = None
    success = False
    if (status_id and priority_id and type_id):
        if version_id:
            version = BugVersion.objects.get(id=version_id)
        priority = BugPriority.objects.get(id=priority_id)
        bug_type = BugType.objects.get(id=type_id)
        status = BugStatus.objects.get(id = status_id)
        form = FoundBugForm(data=request.POST or None)
        if not request.user.is_anonymous():
            upload_form = FoundbugUploadForm(data=request.POST or None)
        else:
            upload_form = None
        if request.method == 'POST':
            if form.is_valid():
                bug = form.save(commit=False)
                bug.bug_type = bug_type
                bug.priority = priority
                bug.status = status
                if not request.user.is_anonymous():
                    bug.reporter = request.user
                bug.environment = '*Location*:' + request.META['PATH_INFO'] 
                bug.environment += '\n*User-Agent*:' + request.META['HTTP_USER_AGENT'] 
                if 'HTTP_REFERER' in request.META: 
                    bug.environment += '\n*Referer*:' + request.META['HTTP_REFERER'] 
                bug.save()
                if exception:
                    bug_exception = BugException(bug=bug, exception_message=exception)
                    bug_exception.save()
                if version_id:
                    bug_version = VersionBug(bug=bug, version=version)
                    bug_version.save()
                if upload_form and ('file' in request.FILES):
                    uploaded_file = request.FILES['file']
                    if uploaded_file:
                        bug_file = BugUploadedFile(bug=bug)
                        bug_file.name = uploaded_file.name
                        bug_file.user = request.user
                        bug_file.save()
                        bug_file.body.save(str(bug_file.id) + '_' + bug_file.name, uploaded_file)
                success = True
        else:
            success = True
    else:
        template_name = 'bugtracker/bugtracker_not_set.haml'
    c = RequestContext(request, locals())
    t = loader.get_template(template_name)
    response = t.render(c)
    return HttpResponse( json.dumps({'success': success, 'response': response}) )

class BugAdminViews(object):
    urlizer_class = BugtrackerUrlizer
    
    def __init__(self, prefix='', app_name='admin', decorator=None, urlizer=None, base_template = 'bugtracker/base.html'):
        self.prefix = prefix
        self.decorator = None
        self.base_template = base_template
        self.app_name = app_name
        if urlizer:
            self.urlizer = urlizer(app=app_name)
        else:
            self.urlizer = self.urlizer_class(app=app_name)
            
    def decorate(self, view):
        return self.decorator(view) if self.decorator else view
    
    def read_right(self, model, user):
        return user.is_staff
    
    def write_right(self, model, user):
        if (model == IssueComment) or (model == BugUploadedFile):
            return user.is_staff
        return user.is_superuser
    
    def build_view(self, view):
        return self.decorate(
            view.as_view(
                urlizer=self.urlizer, 
                base_template=self.base_template,
                iframe=1 if self.app_name=='admin' else 0,
                viewer=self
            )
        )
    
    def get_urls(self):
        return patterns(self.prefix, 
            url(r'^main/$', self.build_view(BugsView), name='bugtracker_main'),
            url(r'^list/by_priority/(?P<pk>\d+)/$', self.build_view(BugsByPriorityView), name='bugtracker_by_priority'),
            url(r'^list/by_status/(?P<pk>\d+)/$', self.build_view(BugsByStatusView), name='bugtracker_by_status'),
            url(r'^list/by_component/(?P<pk>\d+)/$', self.build_view(BugsByComponentView), name='bugtracker_by_component'),
            url(r'^list/by_type/(?P<pk>\d+)/$', self.build_view(BugsByTypeView), name='bugtracker_by_type'),
            url(r'^list/by_user/(?P<pk>\d+)/$', self.build_view(BugsByUserView), name='bugtracker_by_user'),
            url(r'^(?P<pk>\d+)/bug/$', self.build_view(BugView), name='bugtracker_bug'),
        )

class VersionsAdminViews(BugAdminViews):
    def get_urls(self):
        return patterns(self.prefix, 
            url(r'^versions/$', self.build_view(VersionsView), name='bugtracker_versions'),
            url(r'^(.+)/version/$', self.build_view(VersionView), name='bugtracker_version'),
        )
