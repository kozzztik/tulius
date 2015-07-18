from django.conf import settings as dj_settings
from django.utils.timezone import now
from django.core.cache import cache
from .models import *
from .forms import IssueResolveForm
from .atlassian.sync import sync_project, sync_all, sync_user, sync_icon_file, sync_comment_to_jira
import os
from django.core.exceptions import PermissionDenied

DEFAULT_VERSION_KEY = 'default version'
DEFAULT_PRIORITY_KEY = 'default priority'
DEFAULT_BUG_TYPE_KEY = 'default bug type'
DEFAULT_BUG_STATUS_KEY = 'default bug status'
PROJECT_DESCRIPTION_KEY = 'project description'
PROJECT_RESOLUTION_STATUS_KEY = 'resolution status'
PROJECT_DEFAULT_RESOLUTION_KEY = 'default resolution'
PROJECT_BUG_AUTOSYNC_KEY = 'bug autosync'
PROJECT_LEAD_KEY = 'project lead'
PROJECT_URL_KEY = 'project url'
PROJECT_NAME_KEY = 'project name'
PROJECT_SMALL_ICON = 'project_small.png'
PROJECT_BIG_ICON = 'project_big.png'

def get_setting(name, default=None, for_update=False, cached=True):
    if cached and not for_update:
        value = cache.get('bugtracker_' + name.replace(' ', '_'))
        if not value is None:
            return value
    settings = BugtrackerSetting.objects.filter(name=name)
    if for_update:
        settings = settings.select_for_update()
    if settings:
        value = settings[0].value
    else:
        value = default
    if cached:
        cache.set('bugtracker_' + name.replace(' ', '_'), str(value))
    return value
    
def set_setting(name, value, cached=True):
    setting = BugtrackerSetting.objects.get_or_create(name=name)[0]
    setting.value = value
    setting.save()
    if cached:
        cache.set('bugtracker_' + name.replace(' ', '_'), str(value))
    
class BugTrackerStatistics():
    def priorites(self):
        return BugPriority.objects.all()
    
    def statuses(self):
        return BugStatus.objects.all()
    
    def bug_types(self):
        return BugType.objects.all()
    
    def jira_users(self):
        return JiraUser.objects.all()
    
    def components(self):
        return BugComponent.objects.all()
    
    def versions(self):
        return BugVersion.objects.all()

    def not_synced_not_solved(self):
        return Bug.objects.not_synced_not_solved()[:10]
    
    def last_updated(self):
        return Bug.objects.last_updated()[:10]

    def project_name(self):
        return get_setting(PROJECT_NAME_KEY)
    
    def project_description(self):
        return get_setting(PROJECT_DESCRIPTION_KEY)
    
    def project_url(self):
        return get_setting(PROJECT_URL_KEY)
    
    def project_lead(self):
        lead_id = get_setting(PROJECT_LEAD_KEY)
        return JiraUser.objects.get(id=int(lead_id))
    
    def project_small_icon(self):
        return dj_settings.MEDIA_URL + BUGTRACKER_MEDIA + PROJECT_SMALL_ICON
    
    def project_big_icon(self):
        return dj_settings.MEDIA_URL + BUGTRACKER_MEDIA + PROJECT_BIG_ICON
    
def do_sync_project():
    answer = sync_project()
    set_setting(PROJECT_DESCRIPTION_KEY, answer['description'])
    set_setting(PROJECT_LEAD_KEY, sync_user(answer['lead']))
    set_setting(PROJECT_URL_KEY, answer['url'] if 'url' in answer else '')
    set_setting(PROJECT_NAME_KEY, answer['name'])
    media_root = getattr(dj_settings, 'MEDIA_ROOT', None)
    if media_root:
        media_root += BUGTRACKER_MEDIA
        try:
            os.makedirs(media_root)
        except:
            pass
        sync_icon_file(answer['avatarUrls']['16x16'], media_root + PROJECT_SMALL_ICON)
        sync_icon_file(answer['avatarUrls']['48x48'], media_root + PROJECT_BIG_ICON)

def do_sync_all():
    do_sync_project()
    sync_all()
    
def get_resolve_form():
    resolution = get_setting(PROJECT_DEFAULT_RESOLUTION_KEY)
    return IssueResolveForm(initial={'resolution': resolution})

def resolve_issue(issue, resolution):
    issue.resolution = resolution
    status_id = get_setting(PROJECT_RESOLUTION_STATUS_KEY)
    if status_id:
        status = BugStatus.objects.get(id=status_id)
    issue.status = status
    issue.updated_time = now()
    issue.resolution_time = now()
    issue.save()

def reopen_issue(issue):
    issue.resolution = None
    status_id = get_setting(DEFAULT_BUG_STATUS_KEY)
    if status_id:
        status = BugStatus.objects.get(id=status_id)
    issue.status = status
    issue.updated_time = now()
    issue.resolution_time = None
    issue.save()
    
def add_comment(issue, user, comment):
    if not user.is_authenticated():
        raise PermissionDenied()
    issue_comment = IssueComment(bug=issue, user=user, body=comment)
    issue_comment.save()
    sync_comment_to_jira(issue_comment)
