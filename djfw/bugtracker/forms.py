from django.utils.translation import ugettext as _
from django import forms
from .models import BugVersion, BugStatus, BugType, BugPriority, Bug, BugResolution

class CreateBugSettingform(forms.Form):
    bug_type = forms.ModelChoiceField(
        required = False,
        queryset = BugType.objects.all(),
        label = _(u'bug type'),
    )
    bug_priority = forms.ModelChoiceField(
        required = False,
        queryset = BugPriority.objects.all(),
        label = _(u'priority'),
    )
    bug_version = forms.ModelChoiceField(
        required = False,
        queryset = BugVersion.objects.filter(released=False),
        label = _(u'version'),
    )
    bug_status = forms.ModelChoiceField(
        required = False,
        queryset = BugStatus.objects.all(),
        label = _(u'status'),
    )
    
class OtherSettingsForm(forms.Form):
    resolution_status = forms.ModelChoiceField(
        required = False,
        queryset = BugStatus.objects.all(),
        label = _(u'resolution status'),
    )
    
    default_resolution = forms.ModelChoiceField(
        required = False,
        queryset = BugResolution.objects.all(),
        label = _(u'default resolution'),
    )
    
    do_bug_auto_sync  = forms.BooleanField(
        required = False,
        label = _(u'autosync bug on view'),
    )

class IssueAddCommentForm(forms.Form):
    comment = forms.CharField(
        label = _(u'comment'),
        required = False,
        widget = forms.Textarea(attrs={'class': 'mceNoEditor'}),
    )
    
class IssueAttachFileForm(IssueAddCommentForm):
    file  = forms.FileField(
        required = False,
        label = _(u'file'),
    )

class IssueResolveForm(IssueAddCommentForm):
    resolution = forms.ModelChoiceField(
        required = True,
        queryset = BugResolution.objects.all(),
        empty_label=None,
        label = _(u'resolution'),
    )

class IssueReopenForm(IssueAddCommentForm):
    pass

class FoundBugForm(forms.ModelForm):
    class Meta:
        model = Bug
        fields=('summary', 'description', )
        widgets = {
            'description': forms.Textarea(),
        }
        
class FoundbugUploadForm(forms.Form):
    file  = forms.FileField(
        required = False,
        label = _(u'attach file'),
    )