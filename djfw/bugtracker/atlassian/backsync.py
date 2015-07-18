def post_issue(issue):
    fields = {}
    fields['summary'] = issue.summary
    fields['issuetype'] = {'id': str(issue.bug_type.jiraid)}
    fields['priority'] = {'id': str(issue.priority.jiraid)}
    fields['environment'] = issue.environment
    fields['description'] = issue.description
    fields['versions'] = [{'id': str(version.version.jiraid)} for version in issue.versions.all()]
    fields['components'] = [{'id': str(component.component.jiraid)} for component in issue.components.all()]
    return fields

def post_comment(comment):
    body = comment.body
    if comment.user:
        body = "#%s\n%s" % (comment.user.username, body)
    return {'body': body}