from django.views.generic import TemplateView, ListView, DetailView
from django.utils.translation import ugettext_lazy as _
from django.http import Http404, HttpResponseRedirect
from django.utils.encoding import force_unicode
from .forms import IssueAttachFileForm
from .core import *
from .atlassian.sync import sync_existing_issue, sync_issue_to_jira
from .forms import IssueReopenForm, IssueAddCommentForm, CreateBugSettingform, OtherSettingsForm
from .urlizer import BugtrackerUrlizer

class UrlizedViewMixin(object):
    urlizer = BugtrackerUrlizer()
    base_template = 'bugtracker/base.html'
    iframe = 1
    viewer = None
    
    def read_right(self):
        model = getattr(self, 'model', None)
        return self.viewer.read_right(model, self.request.user)
    
    def write_right(self):
        model = getattr(self, 'model', None)
        return self.viewer.write_right(model, self.request.user)
    
    def get_context_data(self, **kwargs):
        if not self.read_right():
            raise Http404('No read right')
        context = super(UrlizedViewMixin, self).get_context_data(**kwargs)
        context['urlizer'] = self.urlizer
        context['base_template'] = self.base_template
        context['iframe'] = self.iframe
        context['write_right'] = self.write_right()
        return context

class BugsView(UrlizedViewMixin, TemplateView):
    template_name = 'bugtracker/main.html'
    
    def get_context_data(self, **kwargs):
        context = super(BugsView, self).get_context_data(**kwargs)
        context['statistics'] = BugTrackerStatistics()
        return context

class SettingsView(TemplateView):
    template_name = 'bugtracker/settings.html'
    model = None
    
    def get_context_data(self, **kwargs):
        if not self.request.user.is_superuser:
            raise Http404()
        s_init={}
        b_init={}
        context = TemplateView.get_context_data(self, **kwargs)
        b_init['bug_version'] = get_setting(DEFAULT_VERSION_KEY)
        b_init['bug_priority'] = get_setting(DEFAULT_PRIORITY_KEY)
        b_init['bug_type'] = get_setting(DEFAULT_BUG_TYPE_KEY)
        b_init['bug_status'] = get_setting(DEFAULT_BUG_STATUS_KEY)
        s_init['resolution_id'] = get_setting(PROJECT_RESOLUTION_STATUS_KEY)
        s_init['do_bug_auto_sync'] = get_setting(PROJECT_BUG_AUTOSYNC_KEY) == 'True'
        s_init['default_resolution'] = get_setting(PROJECT_DEFAULT_RESOLUTION_KEY)
        self.bug_settings = CreateBugSettingform(data=self.request.POST or None, initial=b_init)
        self.other_settings = OtherSettingsForm(data=self.request.POST or None, initial=s_init)
        context['bug_settings'] = self.bug_settings
        context['other_settings'] = self.other_settings
        opts = self.model._meta
        context['app_label'] = opts.app_label
        context['opts'] = opts
        context['title'] = self.model._meta.verbose_name_plural
        return context
    
    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if self.bug_settings.is_valid() and self.other_settings.is_valid():
            version = self.bug_settings.cleaned_data['bug_version']
            priority = self.bug_settings.cleaned_data['bug_priority']
            bug_type = self.bug_settings.cleaned_data['bug_type']
            bug_status = self.bug_settings.cleaned_data['bug_status']
            resolution = self.other_settings.cleaned_data['resolution_status']
            default_resolution = self.other_settings.cleaned_data['default_resolution']
            bug_autosync = self.other_settings.cleaned_data['do_bug_auto_sync']
            set_setting(DEFAULT_VERSION_KEY, version.id if version else None)
            set_setting(DEFAULT_PRIORITY_KEY, priority.id if priority else None)
            set_setting(DEFAULT_BUG_TYPE_KEY, bug_type.id if bug_type else None)
            set_setting(DEFAULT_BUG_STATUS_KEY, bug_status.id if bug_status else None)
            set_setting(PROJECT_RESOLUTION_STATUS_KEY, resolution.id if resolution else None)
            set_setting(PROJECT_DEFAULT_RESOLUTION_KEY, default_resolution.id if default_resolution else None)
            set_setting(PROJECT_BUG_AUTOSYNC_KEY, bug_autosync if bug_autosync else False)
        return self.render_to_response(context)

class VersionsView(UrlizedViewMixin, ListView):
    template_name = 'bugtracker/versions.html'
    model = BugVersion

class VersionView(UrlizedViewMixin, DetailView):
    template_name = 'bugtracker/version.html'
    model = BugVersion
    
    def get_object(self, queryset=None):
        self.kwargs['pk'] = self.args[0]
        return super(VersionView, self).get_object(queryset)
    
    def get_context_data(self, **kwargs):
        context = super(VersionView, self).get_context_data(**kwargs)
        issues = [version.bug for version in self.object.issues()]
        context['solved'] = [issue for issue in issues if issue.resolution_time]
        context['not_solved'] = [issue for issue in issues if not issue.resolution_time]
        context['issues'] = issues
        context['title'] = 'sdsf'
        return context
    
class AdminProxyView(TemplateView):
    modeladmin=None
    template_name = 'admin/bugtracker/bug/list_proxy.html'
    def get_context_data(self, **kwargs):
        opts = self.modeladmin.model._meta
        app_label = opts.app_label
        proxy_filter = self.request.GET['filter']
        proxy_id = self.request.GET['id']
        return {
            'module_name': force_unicode(opts.verbose_name_plural),
            'title': 'Bugs',
            'opts': opts,
            'has_add_permission': self.modeladmin.has_add_permission(self.request),
            'app_label': app_label,
            'proxy_filter': proxy_filter,
            'proxy_id': proxy_id,
            'urlizer': BugtrackerUrlizer(),
        }

class BugsByPriorityView(UrlizedViewMixin, DetailView):
    template_name = 'bugtracker/issue_list.html'
    model = BugPriority
    sub_queryset = Bug.objects.unsolved_by_priority
    page_caption = _('Unresolved issues with priority %s')
    
    def get_page_caption(self):
        return self.page_caption % unicode(self.object)

    def get_context_data(self, **kwargs):
        context = super(BugsByPriorityView, self).get_context_data(**kwargs)
        context['issues'] = self.sub_queryset(self.object)
        context['page_caption'] = self.get_page_caption()
        return context
    
class BugsByStatusView(BugsByPriorityView):
    model = BugStatus
    sub_queryset = Bug.objects.unsolved_by_status
    page_caption = _('Unresolved issues with status %s')

class BugsByComponentView(BugsByPriorityView):
    model = BugComponent
    sub_queryset = Bug.objects.unsolved_by_component
    page_caption = _('Unresolved issues of %s')
    
class BugsByTypeView(BugsByPriorityView):
    model = BugType
    sub_queryset = Bug.objects.unsolved_by_type
    page_caption = _('Unresolved issues of type %s')
    
class BugsByUserView(BugsByPriorityView):
    model = JiraUser
    sub_queryset = Bug.objects.unsolved_by_assignee
    page_caption = _('Unresolved issues of %s')
    
class BugView(UrlizedViewMixin, DetailView):
    template_name = 'bugtracker/issue.html'
    model = Bug
    context_object_name = 'issue'
    
    def get_context_data(self, **kwargs):
        context = super(BugView, self).get_context_data(**kwargs)
        if (get_setting(PROJECT_BUG_AUTOSYNC_KEY) == 'True') and self.object.jira_url:
            sync_existing_issue(self.object)
        user = self.request.user
        if self.viewer.write_right(BugUploadedFile, user):
            context['attach_file_form'] = IssueAttachFileForm()
        if self.write_right():
            context['resolve_issue_form'] = get_resolve_form()
            context['reopen_issue_form'] = IssueReopenForm()
        if self.viewer.write_right(IssueComment, user):
            context['add_comment_form'] = IssueAddCommentForm()
        return context
    
    def get(self, request, *args, **kwargs):
        if 'action' in request.GET:
            return self.post(request, *args, **kwargs)
        return super(BugView, self).get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        action = request.GET['action']
        comment = None
        user = self.request.user
        if action == 'post_to_jira' and self.write_right():
            sync_issue_to_jira(request, obj)
        elif action == 'attach_file' and self.viewer.write_right(BugUploadedFile, user):
            upload_form = IssueAttachFileForm(data=request.POST or None)
            if upload_form.is_valid() and ('file' in request.FILES):
                uploaded_file = request.FILES['file']
                comment = upload_form.cleaned_data['comment']
                if uploaded_file:
                    issue_file = BugUploadedFile(bug=obj)
                    issue_file.name = uploaded_file.name
                    issue_file.user = request.user
                    issue_file.save()
                    issue_file.body.save(str(issue_file.id) + '_' + issue_file.name, uploaded_file)
        elif action == 'resolve' and self.write_right():
            resolve_form = IssueResolveForm(data=request.POST or None)
            if resolve_form.is_valid():
                comment = resolve_form.cleaned_data['comment']
                resolution = resolve_form.cleaned_data['resolution']
                resolve_issue(obj, resolution)
        elif action == 'reopen' and self.write_right():
            reopen_form = IssueReopenForm(data=request.POST or None)
            if reopen_form.is_valid():
                comment = reopen_form.cleaned_data['comment']
                reopen_issue(obj)
        elif action == 'add_comment' and self.viewer.write_right(IssueComment, user):
            add_comment_form = IssueAddCommentForm(data=request.POST or None)
            if add_comment_form.is_valid():
                comment = add_comment_form.cleaned_data['comment']
        elif action == 'sync' and self.write_right():
            if obj.jira_url:
                sync_existing_issue(obj)
        if comment:
            add_comment(obj, request.user, comment)
        return HttpResponseRedirect(self.urlizer.bug(obj.id) + 'bug/')
