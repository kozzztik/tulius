from django.utils.translation import ugettext_lazy as _
from djfw.bugtracker.models import Bug
from djfw.logger.models import ExceptionMessage
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.contrib.auth.models import User
from django.views.generic.detail import DetailView
from django.views.generic import ListView
from django.core.urlresolvers import reverse_lazy, reverse

from django.utils.decorators import method_decorator
from .models import SiteUpdate, SiteUpdateIssues
from django.contrib.syndication.views import Feed
from tulius.bugs.urlizer import TuliusBugtrackerUrlizer
from django.views.generic.base import TemplateView

class SiteUpdatesFeed(Feed):
    title = _("Tulius updates feed")
    link = reverse_lazy("bugs:updates_feed")
    description = "Programming updates of Tulius.com"

    def items(self):
        return SiteUpdate.objects.order_by('-id')[:20]

    def item_title(self, item):
        return _("Update revision %s") % item.revision

    def item_description(self, item):
        issue_links = item.issues.all()
        if not issue_links:
            return _("No update information provided.")
        issues = [link.issue for link in issue_links]
        return "\n".join(['<a href="%s">%s</a> %s' % (reverse("bugs:bugtracker_bug", args=(issue.id,)), issue.jira_key, issue.summary) for issue in issues])
    
    def item_pubdate(self, item):
        return item.start_time
    
class UserExceptions(DetailView):
    model = User
    template_name='bugs/user_exceptions.haml'
    pk_url_kwarg = 'user_id'

    def get_context_data(self, **kwargs):
        if not self.request.user.is_superuser:
            raise Http404()
        sel_user = self.get_object()
        exceptions = ExceptionMessage.objects.filter(user=sel_user)
        return locals()
    
    @method_decorator(login_required)
    def get(self, *args, **kwargs):
        return super(UserExceptions, self).get(*args, **kwargs)

class SiteUpdates(ListView):
    model = SiteUpdate
    template_name='bugs/site_updates.haml'
    
from djfw.bugtracker.views import BugAdminViews
from djfw.bugtracker.models import IssueComment, BugUploadedFile

class MyBugAdminViews(BugAdminViews):
    def read_right(self, model, user):
        return True
    
    def write_right(self, model, user):
        if (model == IssueComment) or (model == BugUploadedFile):
            return True
        return user.is_superuser
issue_views = MyBugAdminViews(app_name='bugs', base_template='bugs/base.html')

class ComplaintsView(TemplateView):
    template_name='bugs/bug_list.haml'
    def get_context_data(self, **kwargs):
        if not self.request.user.is_superuser:
            raise Http404()
        issues = Bug.objects.filter(jiraid=0, resolution_time__isnull=True).order_by('create_time')
        urlizer = issue_views.urlizer
        page_caption = unicode(_('Complaints'))
        return locals()

def maint_updated(sender, **kwargs):
    worker = kwargs['worker']
    worker.log('Creating update changeset')
    site_update = SiteUpdate(revision=sender.revision, start_time=sender.start_time, end_time=sender.end_time)
    site_update.save()
    from djfw.installer.models import MaintainceChangelist
    from djfw.bugtracker.core import get_setting, PROJECT_NAME_KEY
    project_name = get_setting(PROJECT_NAME_KEY, None)
    project_name = project_name.upper()
    if not project_name:
        worker.log('Bugtracker project name not set. No issues will be parsed.')
        return
    import re
    pattern = project_name + ur'-(?P<id>\d+)'
    reg = re.compile(pattern)
    changeset = MaintainceChangelist.objects.filter(mainteince=sender)
    revisions = [change.revision for change in changeset]
    all_nums = {}
    for revision in revisions:
        nums = reg.findall(revision.comment)
        for num in nums:
            all_nums[num] = '1'
    for num in all_nums.keys():
        try:
            issue = Bug.objects.get(jira_key="%s-%s" % (project_name, num))
            SiteUpdateIssues(update=site_update, issue=issue).save()
        except Bug.DoesNotExist:
            pass