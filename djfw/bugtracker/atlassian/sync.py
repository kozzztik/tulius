from django.core.files.base import ContentFile
from .syncbug import sync_bug, sync_user, sync_comments
from django.conf import settings as dj_settings
from djfw.bugtracker.models import *
from .backsync import post_issue, post_comment
import os
from .jiraconnection import JiraConnector
from djfw.httplib.iso8601 import parse_date

class BugTrackerNotSet(Exception):
    pass

class BugTrackerRequestFailed(Exception):
    pass

settings = None

def get_setting(name):
    global settings
    if not settings:
        settings = getattr(dj_settings, 'BUGTRACKER', None)
    if not settings:
        raise BugTrackerNotSet('Bugtracker not set in settings.py')
    if not name in settings:
        raise BugTrackerNotSet('Bugtracker %s not set in settings.py' % (name,))
    return settings[name]
        
jira = JiraConnector(get_setting('url'), get_setting('login'), get_setting('password'), get_setting('project'),
                     get_setting('ca_certs'), get_setting('disable_certs'))

def sync_icon(url, field, prefix):
    content = jira.request(url, absolute_url=True)
    if field.name <> '':
        field.delete()
    field.save(str(prefix) + '.png', ContentFile(content))

def sync_prioritets():
    answer = jira.priorities_list()
    for priority in answer:
        icon_url = priority[u'iconUrl']
        url = priority[u'self']
        pr_obj_list = BugPriority.objects.filter(url=url)
        if pr_obj_list.count() > 0:
            pr_obj = pr_obj_list[0]
        else:
            pr_obj = BugPriority(url=url)
        pr_obj.name = priority[u'name']
        pr_obj.description = priority[u'description']
        pr_obj.status_color = priority[u'statusColor']
        pr_obj.jiraid = priority[u'id']
        pr_obj.save()
        sync_icon(icon_url, pr_obj.icon, pr_obj.pk)

def sync_bug_types():
    answer = jira.issue_types_list()
    for bug_type in answer:
        icon_url = bug_type[u'iconUrl']
        url = bug_type[u'self']
        jiraid = bug_type[u'id']
        bug_obj_list = BugType.objects.filter(jiraid=jiraid)
        if bug_obj_list.count() > 0:
            bug_obj = bug_obj_list[0]
        else:
            bug_obj = BugType(jiraid=jiraid)
        bug_obj.name = bug_type[u'name']
        bug_obj.description = bug_type[u'description']
        bug_obj.subtask = bug_type[u'subtask']
        bug_obj.url = url
        bug_obj.save()
        sync_icon(icon_url, bug_obj.icon, bug_obj.pk)
        
def sync_bug_status():
    answer = jira.statuses_list()
    for bug_status in answer:
        icon_url = bug_status[u'iconUrl']
        url = bug_status[u'self']
        jiraid = bug_status[u'id']
        bug_obj_list = BugStatus.objects.filter(jiraid=jiraid)
        if bug_obj_list.count() > 0:
            bug_obj = bug_obj_list[0]
        else:
            bug_obj = BugStatus(jiraid=jiraid)
        bug_obj.name = bug_status[u'name']
        bug_obj.description = bug_status[u'description']
        bug_obj.url = url
        bug_obj.save()
        sync_icon(icon_url, bug_obj.icon, bug_obj.pk)
        
def sync_bug_resolutions():
    answer = jira.resolutions_list()
    for bug_resolution in answer:
        url = bug_resolution[u'self']
        bug_obj_list = BugResolution.objects.filter(url=url)
        if bug_obj_list.count() > 0:
            bug_obj = bug_obj_list[0]
        else:
            bug_obj = BugResolution(url=url)
        bug_obj.name = bug_resolution[u'name']
        bug_obj.description = bug_resolution[u'description']
        bug_obj.save()

def sync_bug_components():
    answer = jira.components_list()
    for component in answer:
        url = component[u'self']
        jiraid = component[u'id']
        bug_obj_list = BugComponent.objects.filter(jiraid=jiraid)
        if bug_obj_list.count() > 0:
            bug_obj = bug_obj_list[0]
        else:
            bug_obj = BugComponent(jiraid=jiraid)
        bug_obj.name = component[u'name']
        bug_obj.description = component[u'description']
        bug_obj.url = url
        bug_obj.assignee_type = component[u'assigneeType']
        bug_obj.real_assignee_type = component[u'realAssigneeType']
        bug_obj.isAssigneeTypeValid = component[u'isAssigneeTypeValid']
        bug_obj.lead = sync_user(component[u'lead'])
        bug_obj.assignee = sync_user(component[u'assignee'])
        bug_obj.real_assignee = sync_user(component[u'realAssignee'])
        bug_obj.save()

def sync_bug_link_type():
    answer = jira.link_types_list()
    for link_type in answer:
        url = link_type[u'self']
        jiraid = link_type[u'id']
        bug_obj_list = BugLinkType.objects.filter(jiraid=jiraid)
        if bug_obj_list.count() > 0:
            bug_obj = bug_obj_list[0]
        else:
            bug_obj = BugLinkType(jiraid=jiraid)
        bug_obj.name = link_type[u'name']
        bug_obj.inward = link_type[u'inward']
        bug_obj.outward = link_type[u'outward']
        bug_obj.url = url
        bug_obj.save()

def sync_bug_list(versions=None):
    if not versions:
        versions = BugVersion.objects.filter(archived=False)
    for version in versions:
        answer = jira.issue_by_version(version.name)
        for bug in answer:
            bug_data = jira.request_json(bug['self'], absolute_url=True) 
            sync_bug(bug_data)
            
def sync_bug_version():
    answer = jira.versions_list()
    resync_versions = []
    for bug_verion in answer:
        url = bug_verion[u'self']
        jiraid = bug_verion[u'id']
        bug_obj_list = BugVersion.objects.filter(jiraid=jiraid)
        if bug_obj_list.count() > 0:
            bug_obj = bug_obj_list[0]
            old_archived = bug_obj.archived
        else:
            bug_obj = BugVersion(jiraid=jiraid)
            old_archived = False
        bug_obj.name = bug_verion[u'name']
        if 'description' in bug_verion:
            bug_obj.description = bug_verion[u'description']
        else:
            bug_obj.description = ''
        bug_obj.url = url
        bug_obj.released = bug_verion[u'released']
        if bug_obj.released:
            bug_obj.release_date = parse_date(bug_verion[u'releaseDate'] + ' 00:00:00')
        if 'userReleaseDate' in bug_verion:
            bug_obj.user_release_date = bug_verion[u'userReleaseDate']
        bug_obj.archived = bug_verion[u'archived']
        if bug_obj.archived and not (old_archived):
            resync_versions += [bug_obj]
        bug_obj.save()
    if resync_versions:
        sync_bug_list(resync_versions)
        
def do_assync_bug_sync():
    import threading
    t = threading.Thread(target=sync_bug_list)
    t.daemon = True
    t.start()

def sync_existing_issue(issue):
    answer = jira.request_json(issue.jira_url, absolute_url=True)
    sync_bug(answer)
    
def sync_users():
    users_list = JiraUser.objects.all()
    for user_obj in users_list:
        answer = jira.request_json(user_obj.jira_url, absolute_url=True)
        user_obj.email = answer['emailAddress']
        user_obj.display_name = answer['displayName']
        user_obj.active = answer['active']
        sync_icon(answer['avatarUrls']['48x48'], user_obj.big_icon, str(user_obj.jiraid))
        sync_icon(answer['avatarUrls']['16x16'], user_obj.small_icon, str(user_obj.jiraid))
        user_obj.save()

def sync_icon_file(url, path):
    content = jira.request(url, absolute_url=True)
    if os.path.exists(path):
        os.remove(path)
    f = open(path, 'wb')
    f.write(content)
    f.close()
    
def sync_project():
    return jira.project_info()
    
def sync_comment_to_jira(comment):
    if not comment.bug.jiraid:
        return
    answer = jira.post_comment(comment.bug.jiraid, post_comment(comment))
    comment.jiraid = answer['id']
    comment.save()
    sync_comments(comment.bug, [answer])
    
def sync_issue_to_jira(request, issue):
    if issue.jiraid:
        return
    referer = request.META['HTTP_REFERER'] 
    if referer: 
        issue.environment += '\n*Issue*:[%s]' % (referer,)
    answer = jira.post_issue(post_issue(issue))
    issue.jiraid = answer['id']
    issue.jira_url = answer['self']
    issue.jira_key =  answer['key']
    issue.save()
    for comment in issue.comments.all():
        sync_comment_to_jira(comment)

def sync_all():
    sync_prioritets()
    sync_bug_types()
    sync_bug_status()
    sync_bug_resolutions()
    sync_bug_version()
    sync_bug_link_type()
    sync_bug_components()
    sync_bug_list()
    sync_users()
