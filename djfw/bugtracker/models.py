from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.conf import settings
    
BUGTRACKER_MEDIA = 'bugtracker/'

class BugType(models.Model):
    """
    Bug types imported from Jira
    """
    
    class Meta:
        verbose_name = _('bug type')
        verbose_name_plural = _('bug types')
        ordering = ['name']
        
    jiraid = models.IntegerField(
        default=0,
        verbose_name=u'Jira ID',
    )
    
    name = models.CharField(
        max_length=100, 
        unique=False, 
        verbose_name=_('name')
    )
    
    url = models.CharField(
        max_length=100, 
        unique=False, 
        verbose_name='URL'
    )
    
    subtask = models.BooleanField(
        blank=False,
        null=False,
        default=False,
        verbose_name=_(u'subtask'),
    )
    
    icon = models.FileField(
        blank=True,
        null=True,
        verbose_name=_(u'icon'),
        upload_to=BUGTRACKER_MEDIA + 'bugtype_icon',
    )
    
    def __unicode__(self):
        return self.name
    
    def not_solved(self):
        return Bug.objects.not_solved().filter(bug_type=self)
     
    def not_solved_percent(self):
        return (self.not_solved().count() * 100) / Bug.objects.not_solved().count() 

class BugPriority(models.Model):
    """
    Bug priority imported from Jira
    """
    
    class Meta:
        verbose_name = _('bug priority')
        verbose_name_plural = _('bug priority')
    
    status_color = models.CharField(
        max_length=10, 
        unique=False, 
        verbose_name=_('status color')
    )
    
    name = models.CharField(
        max_length=100, 
        unique=False, 
        verbose_name=_('name')
    )
    
    description = models.CharField(
        max_length=100, 
        unique=False, 
        verbose_name=_('description')
    )
    
    url = models.CharField(
        max_length=100, 
        unique=True, 
        verbose_name='URL'
    )
    
    icon = models.FileField(
        blank=True,
        null=True,
        verbose_name=_(u'icon'),
        upload_to=BUGTRACKER_MEDIA + 'bugpriority_icon',
    )
    
    jiraid = models.IntegerField(
        default=0,
        verbose_name=u'Jira ID',
    )

    def __unicode__(self):
        return self.name
    
    def not_solved(self):
        return Bug.objects.not_solved().filter(priority=self)
    
    def not_solved_percent(self):
        return (self.not_solved().count() * 100) / Bug.objects.not_solved().count() 

class BugVersion(models.Model):
    """
    Bug version imported from Jira
    """
    
    class Meta:
        verbose_name = _('bug version')
        verbose_name_plural = _('bug versions')
        ordering = ['-name']
        
    name = models.CharField(
        max_length=100, 
        unique=False, 
        verbose_name=_('name')
    )
    
    description = models.CharField(
        max_length=100, 
        unique=False, 
        verbose_name=_('description')
    )
    
    url = models.CharField(
        max_length=100, 
        unique=False, 
        verbose_name='URL'
    )
    
    jiraid = models.IntegerField(
        unique=True, 
        default=0,
        verbose_name=u'Jira ID',
    )
    
    released = models.BooleanField(
        default=False,
        verbose_name=u'released',
    )
    
    release_date = models.DateTimeField(
        blank=True,
        null=True,
        auto_now_add    = False,
        verbose_name    = _('release date'),
    )
    
    archived = models.BooleanField(
        default=False,
        verbose_name=u'archived',
    )
    
    show = models.BooleanField(
        default=False,
        verbose_name=u'show',
    )
        
    user_release_date = models.CharField(
        max_length=50, 
        unique=False, 
        verbose_name    = _('user release date'),
    )
    
    def __unicode__(self):
        return self.name
    
    def issues(self, **kwargs):
        return BugFixVersion.objects.filter(version=self, **kwargs).select_related('bug').order_by('bug__priority__jiraid')
    
    def not_solved(self):
        return self.issues(bug__resolution_time__isnull=True)
    
    def solved(self):
        return self.issues(bug__resolution_time__isnull=False)
    
    def all_issues(self):
        return self.issues()
    
    def solved_percent(self):
        count = self.all_issues().count() 
        if count:
            return (self.solved().count() * 100) / count
        else:
            return 100 
    
class BugStatus(models.Model):
    """
    Bug statuses imported from Jira
    """
    class Meta:
        verbose_name = _('bug status')
        verbose_name_plural = _('bug statuses')

    name = models.CharField(
        max_length=100, 
        unique=False, 
        verbose_name=_('name')
    )
    
    description = models.CharField(
        max_length=255, 
        unique=False, 
        verbose_name=_('description')
    )
    
    url = models.CharField(
        max_length=100, 
        unique=False, 
        verbose_name='URL'
    )
    
    jiraid = models.IntegerField(
        unique=True, 
        default=0,
        verbose_name=u'Jira ID',
    )
    
    icon = models.FileField(
        blank=True,
        null=True,
        verbose_name=_(u'icon'),
        upload_to=BUGTRACKER_MEDIA + 'bugstatus_icon',
    )
    
    def __unicode__(self):
        return self.name
    
    def bug_percent(self):
        return (self.bugs.count() * 100) / Bug.objects.all().count() 

class BugResolution(models.Model):
    """
    Bug resolutions imported from Jira
    """
    class Meta:
        verbose_name = _('bug resolutions')
        verbose_name_plural = _('bug resolutions')

    name = models.CharField(
        max_length=100, 
        unique=False, 
        verbose_name=_('name')
    )
    
    description = models.CharField(
        max_length=100, 
        unique=False, 
        verbose_name=_('description')
    )
    
    url = models.CharField(
        max_length=100, 
        unique=True, 
        verbose_name='URL'
    )
    
    show = models.BooleanField(
        default=False,
        verbose_name=u'do sync',
    )
    
    icon = models.FileField(
        blank=True,
        null=True,
        verbose_name=_(u'icon'),
        upload_to=BUGTRACKER_MEDIA + 'bugresolution_icon',
    )
    
    def __unicode__(self):
        return self.name
    
class BugLinkType(models.Model):
    """
    Bug link types
    """
    class Meta:
        verbose_name = _('bug link type')
        verbose_name_plural = _('bug link types')
    
    jiraid = models.IntegerField(
        unique=True, 
        default=0,
        verbose_name=u'Jira ID',
    )
    
    name = models.CharField(
        max_length=100, 
        unique=False, 
        verbose_name=_('name')
    )
    
    inward = models.CharField(
        max_length=100, 
        unique=False, 
        verbose_name=_('inward')
    )

    outward = models.CharField(
        max_length=100, 
        unique=False, 
        verbose_name=_('outward')
    )
    
    url = models.CharField(
        max_length=100, 
        unique=False, 
        verbose_name='URL'
    )
    
    def __unicode__(self):
        return self.name
    
class JiraUser(models.Model):
    """
    jira user mapping
    """
    class Meta:
        verbose_name = _('user mapping')
        verbose_name_plural = _('user mappings')

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        null=True,
        blank=True,
        related_name='jira_data', 
        verbose_name=_('django user')
    )
    
    jiraid = models.CharField(
        max_length=100, 
        unique=False, 
        verbose_name=u'Jira ID',
        editable=False,
    )
    
    jira_url = models.CharField(
        max_length=100, 
        unique=False, 
        verbose_name=_('jira_url'),
        editable=False,
    )
    
    email = models.CharField(
        max_length=100, 
        unique=False, 
        verbose_name=_('email'),
        editable=False,
    )

    display_name = models.CharField(
        max_length=200, 
        unique=False, 
        verbose_name=_('display name'),
        editable=False,
    )
    
    active = models.BooleanField(
        default=True,
        verbose_name=u'is active',
    )
    
    small_icon = models.ImageField(
        blank=True,
        null=True,
        verbose_name=_(u'small icon'),
        upload_to=BUGTRACKER_MEDIA + 'jira_user_icon_small',
        editable=False,
    )
    
    big_icon = models.ImageField(
        blank=True,
        null=True,
        verbose_name=_(u'big icon'),
        upload_to=BUGTRACKER_MEDIA + 'jira_user_icon_big',
        editable=False,
    )
    
    def __unicode__(self):
        if self.user:
            if self.user.get_full_name():
                return self.user.get_full_name()
            else:
                return unicode(self.user)
        else:
            if self.display_name:
                return self.display_name
            else:
                return self.jiraid
        
    def not_solved(self):
        return Bug.objects.filter(assignee=self, resolution_time__isnull=True)
    
    def not_solved_percent(self):
        return (self.not_solved().count() * 100) / Bug.objects.not_solved().count() 
    
    def small_image_link(self):
        return '<img src="%s" style="margin-right: 10px"/>%s' % (self.small_icon.url, self.display_name)
    
    small_image_link.allow_tags = True
    small_image_link.short_description = _('Jira user')

class BugComponent(models.Model):
    """
    Bug component imported from Jira
    """
    class Meta:
        verbose_name = _('component')
        verbose_name_plural = _('components')

    jiraid = models.IntegerField(
        unique=True, 
        default=0,
        verbose_name=u'Jira ID',
    )
    
    name = models.CharField(
        max_length=100, 
        unique=False, 
        verbose_name=_('name')
    )
    
    description = models.CharField(
        max_length=100, 
        unique=False, 
        verbose_name=_('description')
    )
    
    url = models.CharField(
        max_length=100, 
        unique=True, 
        verbose_name='URL'
    )
    
    show = models.BooleanField(
        default=True,
        verbose_name=u'do sync',
    )
    
    assignee = models.ForeignKey(
        JiraUser, 
        null=True,
        blank=True,
        related_name='components_assigned', 
        verbose_name=_('assignee')
    )
    
    assignee_type = models.CharField(
        max_length=100, 
        unique=False, 
        verbose_name='assignee type'
    )
    
    real_assignee = models.ForeignKey(
        JiraUser, 
        null=True,
        blank=True,
        related_name='components_real_assigned', 
        verbose_name=_('assignee')
    )
    
    real_assignee_type = models.CharField(
        max_length=100, 
        unique=False, 
        verbose_name='real assignee type'
    )
    
    lead = models.ForeignKey(
        JiraUser, 
        null=True,
        blank=True,
        related_name='components_leaded', 
        verbose_name=_('lead')
    )
    
    isAssigneeTypeValid = models.BooleanField(
        default=False,
        verbose_name=u'is assignee type valid',
    )
    
    def __unicode__(self):
        return self.name
    
    def not_solved(self):
        return BugComponentLink.objects.filter(component=self, bug__resolution_time__isnull=True)

class BugManager(models.Manager):
    def not_solved(self):
        return self.filter(resolution_time__isnull = True)
    
    def solved(self):
        return self.filter(resolution_time__isnull = False)
    
    def authored(self, user):
        return self.filter(reporter=user)
    
    def unsolved_by_priority(self, priority):
        return self.not_solved().filter(priority=priority)
    
    def unsolved_by_status(self, status):
        return self.not_solved().filter(status=status)
    
    def unsolved_by_component(self, component):
        linklist = component.not_solved().order_by('bug__priority', '-bug__create_time')
        bugs = [buglink.bug for buglink in linklist]
        return bugs
    
    def unsolved_by_type(self, bug_type):
        return self.not_solved().filter(bug_type=bug_type)
    
    def unsolved_by_version(self, version):
        linklist = version.not_solved().order_by('bug__priority', '-bug__create_time')
        bugs = [buglink.bug for buglink in linklist]
        return bugs

    def solved_by_version(self, version):
        linklist = version.solved().order_by('bug__priority', '-bug__create_time')
        bugs = [buglink.bug for buglink in linklist]
        return bugs

    def all_by_version(self, version):
        linklist = version.all_issues().order_by('bug__priority', '-bug__create_time')
        bugs = [buglink.bug for buglink in linklist]
        return bugs
        
    def unsolved_by_assignee(self, jira_user):
        return self.not_solved().filter(assignee=jira_user)
    
    def not_synced_not_solved(self):
        return self.not_solved().filter(jiraid=0).order_by('priority', '-create_time')
    
    def last_updated(self):
        return self.all().order_by('-updated_time')
    
class Bug(models.Model):
    """
    Bug types imported from Jira
    """
    
    class Meta:
        verbose_name = _('bug')
        verbose_name_plural = _('bugs')
        ordering = ['priority', '-create_time']
        
    objects = BugManager()
    
    bug_type = models.ForeignKey(
        BugType, 
        null=False,
        blank=False,
        related_name='bugs', 
        verbose_name=_('bug type')
    )
    
    priority = models.ForeignKey(
        BugPriority, 
        null=True,
        blank=True,
        related_name='bugs', 
        verbose_name=_('priority')
    )
    
    status = models.ForeignKey(
        BugStatus, 
        null=False,
        blank=False,
        related_name='bugs', 
        verbose_name=_('status')
    )
    
    resolution = models.ForeignKey(
        BugResolution, 
        null=True,
        blank=True,
        related_name='bugs', 
        verbose_name=_('resolution')
    )
    
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        null=True,
        blank=True,
        related_name='bugs_reported', 
        verbose_name=_('reporter')
    )

    jira_reporter = models.ForeignKey(
        JiraUser, 
        null=True,
        blank=True,
        related_name='bugs_reported', 
        verbose_name=_('jira_reporter')
    )
    
    assignee = models.ForeignKey(
        JiraUser, 
        null=True,
        blank=True,
        related_name='bugs_assigned', 
        verbose_name=_('assignee')
    )

    summary = models.CharField(
        max_length=255, 
        unique=False, 
        verbose_name=_('summary')
    )
    
    description = models.TextField(
        verbose_name=_('description')
    )
    
    environment = models.TextField(
        verbose_name=_('environment')
    )
    
    jira_key = models.CharField(
        max_length=100, 
        verbose_name=_('jira key')
    )
    
    jiraid = models.IntegerField(
        default=0,
        verbose_name=u'Jira ID',
    )
    
    jira_url = models.CharField(
        max_length=100, 
        unique=False, 
        verbose_name=_('jira URL')
    )
    
    create_time = models.DateTimeField(
        auto_now_add    = True,
        verbose_name    = _('create time'),
    )
    
    updated_time = models.DateTimeField(
        auto_now_add    = True,
        verbose_name    = _('updated time'),
    )
    
    resolution_time = models.DateTimeField(
        auto_now_add    = False,
        null=True,
        blank=True,
        verbose_name    = _('resolution time'),
    )
    
    def __unicode__(self):
        if self.summary:
            return self.key() + ' '+ self.summary
        else:
            return self.key() + ' '+ self.description
    
    def key(self):
        if self.jira_key:
            return self.jira_key
        else:
            return "LOCAL-%s" % self.id
    
class BugFixVersion(models.Model):
    """
    Bug fix version
    """
    
    class Meta:
        verbose_name = _('bug fix version')
        verbose_name_plural = _('bug fix versions')
        unique_together = ('bug', 'version')
        
    bug = models.ForeignKey(
        Bug, 
        null=False,
        blank=False,
        related_name='fix_versions', 
        verbose_name=_('bug')
    )
    
    version = models.ForeignKey(
        BugVersion, 
        null=False,
        blank=False,
        related_name='bugs_fix', 
        verbose_name=_('version')
    )
    
class VersionBug(models.Model):
    """
    Version bugs
    """
    
    class Meta:
        verbose_name = _('version bug')
        verbose_name_plural = _('versions bugs')
        
    bug = models.ForeignKey(
        Bug, 
        null=False,
        blank=False,
        related_name='versions', 
        verbose_name=_('bug')
    )
    
    version = models.ForeignKey(
        BugVersion, 
        null=False,
        blank=False,
        related_name='bugs', 
        verbose_name=_('version')
    )

class BugLink(models.Model):
    """
    Bug link
    """
    
    class Meta:
        verbose_name = _('bug link')
        verbose_name_plural = _('bug links')
    
    jiraid = models.IntegerField(
        unique=True, 
        default=0,
        verbose_name=u'Jira ID',
    )
    
    link_type = models.ForeignKey(
        BugLinkType, 
        null=False,
        blank=False,
        related_name='links', 
        verbose_name=_('link_type')
    )
    
    outward = models.ForeignKey(
        Bug, 
        null=True,
        blank=True,
        related_name='inward_links', 
        verbose_name=_('outard')
    )

    inward = models.ForeignKey(
        Bug, 
        null=True,
        blank=True,
        related_name='outward_links', 
        verbose_name=_('inward')
    )
    
class BugException(models.Model):
    """
    Bug exceptions
    """
    
    class Meta:
        verbose_name = _('bug exception')
        verbose_name_plural = _('bug exceptions')

    bug = models.ForeignKey(
        Bug, 
        null=False,
        blank=False,
        related_name='exceptions', 
        verbose_name=_('bug')
    )
    
    exception_message_id = models.IntegerField(
        null=False,
        blank=False,
        verbose_name=_('exception')
    )
    
    def exception_message(self):
        try:
            from djfw.logger.models import ExceptionMessage
        except ImportError:
            from logger.models import ExceptionMessage
        return ExceptionMessage.objects.get(id=self.exception_message_id)
    
    def __unicode__(self):
        return "%s - %s" % (unicode(self.bug), unicode(self.exception_message))
        
class BugSubTask(models.Model):
    """
    Bug subtask link
    """
    
    class Meta:
        verbose_name = _('bug subtask')
        verbose_name_plural = _('bug subtask')

    bug = models.ForeignKey(
        Bug, 
        null=False,
        blank=False,
        related_name='subtask', 
        verbose_name=_('bug')
    )
    
    task = models.ForeignKey(
        Bug, 
        null=False,
        blank=False,
        related_name='parent_bug', 
        verbose_name=_('subtask')
    )

class BugComponentLink(models.Model):
    """
    Bug component link
    """
    
    class Meta:
        verbose_name = _('bug component link')
        verbose_name_plural = _('bugs component links')

    bug = models.ForeignKey(
        Bug, 
        null=False,
        blank=False,
        related_name='components', 
        verbose_name=_('bug')
    )
    
    component = models.ForeignKey(
        BugComponent, 
        null=False,
        blank=False,
        related_name='bugs', 
        verbose_name=_('component')
    )
    
class BugUploadedFile(models.Model):
    """
    Bug exceptions
    """
    
    class Meta:
        verbose_name = _('bug exception')
        verbose_name_plural = _('bug exceptions')
    
    name = models.CharField(
        max_length=100, 
        unique=False, 
        verbose_name=_('name')
    )
    
    upload_time = models.DateTimeField(
        auto_now_add    = True,
        verbose_name    = _('upload time'),
    )
    
    bug = models.ForeignKey(
        Bug, 
        null=True,
        blank=True,
        related_name='files', 
        verbose_name=_('bug')
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        null=False,
        blank=False,
        related_name='bug_files', 
        verbose_name=_('user')
    )
    
    body = models.FileField(
        blank=True,
        null=True,
        verbose_name=_(u'icon'),
        upload_to=BUGTRACKER_MEDIA + 'bug_files',
    )
    
    def get_absolute_url(self):
        return self.body.url

class IssueComment(models.Model):
    """
    Issue comment
    """
    
    class Meta:
        verbose_name = _('issue comment')
        verbose_name_plural = _('issues comments')
    
    bug = models.ForeignKey(
        Bug, 
        null=False,
        blank=False,
        related_name='comments', 
        verbose_name=_('bug')
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        null=True,
        blank=True,
        related_name='comments_on_issues', 
        verbose_name=_('user')
    )

    jiraid = models.IntegerField(
        default=0,
        verbose_name=u'Jira ID',
    )

    jira_user = models.ForeignKey(
        JiraUser, 
        null=True,
        blank=True,
        related_name='comments', 
        verbose_name=_('jira user')
    )

    jira_updated_user = models.ForeignKey(
        JiraUser, 
        null=True,
        blank=True,
        related_name='updated_comments', 
        verbose_name=_('jira updated user')
    )

    create_time = models.DateTimeField(
        auto_now_add    = True,
        verbose_name    = _('create time'),
    )
    
    updated_time = models.DateTimeField(
        auto_now_add    = True,
        verbose_name    = _('updated time'),
    )

    body = models.TextField(
        verbose_name=_('body')
    )

    def __unicode__(self):
        return self.body
        
    def get_absolute_url(self):
        return self.bug.get_absolute_url()
    
class IssueAttachment(models.Model):
    """
    Issue attachment
    """
    
    class Meta:
        verbose_name = _('issue attachment')
        verbose_name_plural = _('issues attachments')
    
    bug = models.ForeignKey(
        Bug, 
        null=False,
        blank=False,
        related_name='attachments', 
        verbose_name=_('bug')
    )

    jiraid = models.IntegerField(
        default=0,
        verbose_name=u'Jira ID',
    )
    
    jira_url = models.CharField(
        max_length=255, 
        null=False,
        blank=False,
        unique=False, 
        verbose_name=_('jira url')
    )

    file_name = models.CharField(
        max_length=255, 
        unique=False, 
        verbose_name=_('file name')
    )
    
    jira_user = models.ForeignKey(
        JiraUser, 
        null=False,
        blank=False,
        related_name='attachments', 
        verbose_name=_('jira user')
    )

    create_time = models.DateTimeField(
        auto_now_add    = True,
        verbose_name    = _('create time'),
    )
    
    size = models.IntegerField(
        default=0,
        verbose_name=u'size',
    )
    
    mime_type = models.CharField(
        max_length=50, 
        unique=False, 
        verbose_name=_('MIME type')
    )
    
    content = models.CharField(
        max_length=255, 
        unique=False, 
        verbose_name=_('content')
    )
    
    thumbnail = models.CharField(
        max_length=255, 
        unique=False, 
        verbose_name=_('thumbnail')
    )
    
    def __unicode__(self):
        return self.file_name
    
    def get_absolute_url(self):
        return self.content
    
class BugtrackerSetting(models.Model):
    """
    Bugtracker setting
    """
    class Meta:
        verbose_name = _('setting')
        verbose_name_plural = _('settings')
        
    name = models.CharField(
        max_length=50, 
        default = '',
        blank=True,
        unique=True, 
        verbose_name=_('name')
    )
    
    value = models.CharField(
        max_length=255, 
        blank=True,
        null=True,
        verbose_name=_('value')
    )
    def __unicode__(self):
        return "%s : %s" % (self.name, self.value)
    