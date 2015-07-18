from djfw.bugtracker.models import *
from .iso8601 import parse_date

def sync_user(user_data):
    jiraid = user_data['name']
    jira_user = JiraUser.objects.get_or_create(jiraid=jiraid)[0]
    jira_user.jira_url = user_data['self']
    if not jira_user.user:
        jira_users = User.objects.filter(username=jiraid)
        if jira_users.count() > 0:
            jira_user.user = jira_users[0]
    jira_user.save()
    return jira_user

def sync_comments(bug, comments):
    for comment in comments:
        comment_id = comment['id']
        comment_obj = IssueComment.objects.get_or_create(jiraid=comment_id, bug=bug)[0]
        comment_obj.jira_user = sync_user(comment['author'])
        comment_obj.jira_updated_user = sync_user(comment['updateAuthor'])
        body = comment['body']
        if body[:1] == "#":
            body = "".join(body.splitlines(True)[1:])
        comment_obj.body = body
        comment_obj.create_time = parse_date(comment['created'])
        comment_obj.updated_time = parse_date(comment['updated'])
        comment_obj.save()
        
def sync_attachments(bug, attachments):
    attachment_list = IssueAttachment.objects.filter(bug=bug)
    for attachment in attachment_list:
        for lookup_attachment in attachments:
            if lookup_attachment['id'] == attachment.jiraid:
                break
        else:
            attachment.delete()
    for attachment in attachments:
        jiraid = int(attachment['id'])
        attachment_obj_list = IssueAttachment.objects.filter(bug=bug, jiraid = jiraid)
        if attachment_obj_list.count() == 0:
            attachment_obj = IssueAttachment(bug=bug, jiraid=jiraid)
            attachment_obj.jira_url = attachment['self']
            attachment_obj.jira_user = sync_user(attachment['author'])
            attachment_obj.file_name = attachment['filename']
            attachment_obj.create_time = parse_date(attachment['created'])
            attachment_obj.size = int(attachment['size'])
            attachment_obj.mime_type = attachment['mimeType']
            attachment_obj.content = attachment['content']
            if 'thumbnail' in attachment:
                attachment_obj.thumbnail = attachment['thumbnail']
            attachment_obj.save()

def sync_bug(bug):
    jiraid = bug['id']
    try:
        bug_obj = Bug.objects.get(jiraid=jiraid)
    except Bug.DoesNotExist:
        bug_obj = Bug(jiraid=jiraid)
    bug_obj.jira_url = bug['self']
    bug_obj.jira_key = bug['key']
    fields = bug['fields']
    
    bug_obj.summary = fields['summary']
    bug_obj.description = fields['description']
    if not bug_obj.description:
        bug_obj.description = ''
    bug_obj.assignee = sync_user(fields['assignee'])
    bug_obj.environment = fields['environment']
    if not bug_obj.environment:
        bug_obj.environment = ''
    if fields['priority']:
        bug_obj.priority = BugPriority.objects.get(url = fields['priority']['self'])
    else:
        bug_obj.priority = None
    bug_obj.status = BugStatus.objects.get(jiraid = fields['status']['id']) 
    bug_obj.updated_time = parse_date(fields['updated'])
    bug_obj.jira_reporter = sync_user(fields['reporter'])
    bug_obj.create_time = parse_date(fields['created'])
    if fields['resolutiondate']:
        bug_obj.resolution_time = parse_date(fields['resolutiondate'])
    else:
        bug_obj.resolution_time = None
    bug_obj.bug_type = BugType.objects.get(jiraid = fields['issuetype']['id']) 
    if fields['resolution']:
        bug_obj.resolution = BugResolution.objects.get(url = fields['resolution']['self'])
    else:
        bug_obj.resolution = None
    bug_obj.save()
    
    subtasks = fields['subtasks']
    subtasks_list = BugSubTask.objects.filter(bug=bug_obj)
    for subtask in subtasks_list:
        for lookup_subtask in subtasks:
            if lookup_subtask['id'] == subtask.task.jiraid:
                break
        else:
            subtask.delete()
    for subtask in subtasks:
        subtask_obj_list = BugSubTask.objects.filter(bug=bug_obj, task__jiraid = subtask['id'])
        if subtask_obj_list.count() == 0:
            subtask_obj = BugSubTask(bug=bug_obj)
            try:
                subtask_obj.task = Bug.objects.get(jiraid = subtask['id'])
                subtask_obj.save()
            except Bug.DoesNotExist:
                pass

    versions = fields['versions']
    version_list = VersionBug.objects.filter(bug=bug_obj)
    for version in version_list:
        for lookup_version in versions:
            if lookup_version['id'] == version.version.jiraid:
                break
        else:
            version.delete()
    for version in versions:
        version_obj_list = VersionBug.objects.filter(bug=bug_obj, version__jiraid = version['id'])
        if version_obj_list.count() == 0:
            version_obj = VersionBug(bug=bug_obj)
            version_obj.version = BugVersion.objects.get(jiraid = version['id'])
            version_obj.save()

    fixVersions = fields['fixVersions']
    version_list = BugFixVersion.objects.filter(bug=bug_obj)
    for version in version_list:
        for lookup_version in fixVersions:
            if lookup_version['id'] == version.version.jiraid:
                break
        else:
            version.delete()
    for version in fixVersions:
        version_obj_list = BugFixVersion.objects.filter(bug=bug_obj, version__jiraid = version['id'])
        if version_obj_list.count() == 0:
            version_obj = BugFixVersion(bug=bug_obj)
            version_obj.version = BugVersion.objects.get(jiraid = version['id'])
            version_obj.save()
    
    components = fields['components']
    components_list = BugComponentLink.objects.filter(bug=bug_obj)
    for component in components_list:
        for lookup_component in components:
            if lookup_component['id'] == component.component.jiraid:
                break
        else:
            component.delete()
    for component in components:
        component_obj_list = BugComponentLink.objects.filter(bug=bug_obj, component__jiraid = component['id'])
        if component_obj_list.count() == 0:
            component_obj = BugComponentLink(bug=bug_obj)
            component_obj.component = BugComponent.objects.get(jiraid = component['id'])
            component_obj.save()
    
    issuelinks =  fields['issuelinks']
    for issuelink in issuelinks:
        linkid = issuelink['id']
        linktype_id = issuelink['type']['id']
        link_type = BugLinkType.objects.get(jiraid = linktype_id)
        link_obj= BugLink.objects.get_or_create(jiraid=linkid, defaults={'link_type': link_type})[0]
        link_obj.link_type = link_type
        if 'outwardIssue' in issuelink:
            link_obj.inward = bug_obj
        else:
            link_obj.outward = bug_obj
        link_obj.save()
        
    comments = fields['comment']['comments']
    sync_comments(bug_obj, comments)
    
    attachments = fields['attachment']
    sync_attachments(bug_obj, attachments)
    pass