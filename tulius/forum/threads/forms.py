from django.utils.translation import ugettext_lazy as _
from django import forms
    
class PostDeleteForm(forms.Form):
    post = forms.IntegerField(
        required = True,
        label = _(u'post'),
        widget=forms.HiddenInput,
    )
    
    message = forms.CharField(
        required = False,
        label = _(u'Delete message'),
        widget=forms.TextInput(attrs={'class':'mceNoEditor'}),
    )
    
class RoomForm(forms.Form):
    title = forms.CharField(
        required = True,
        label = _(u'Title'),
    )
    
    body = forms.CharField(
        required = False,
        label = _(u'Body'),
        widget=forms.widgets.Textarea(),
    )
    
    access_type = forms.ChoiceField(
        required = False,
        label = _(u'Access type'),
    )
    
    def __init__(self, models, thread=None, *args, **kwargs):
        self.caption = _('edit room') if thread else _('add room')
        self.base_fields['access_type'].choices = models.THREAD_ACCESS_TYPE_CHOICES
        self.base_fields['access_type'].initial = models.THREAD_ACCESS_TYPE_NOT_SET
        if thread:
            initial = {}
            initial['title'] = thread.title
            initial['body'] = thread.body
            initial['access_type'] = thread.access_type
            kwargs['initial'] = initial
        super(RoomForm, self).__init__(*args, **kwargs)


class ThreadForm(forms.Form):
    
    title = forms.CharField(
        required = True,
        label = _(u'Title'),
    )
    
    body = forms.CharField(
        required = True,
        label = _(u'Body'),
        widget=forms.widgets.Textarea(),
    )
    
    access_type = forms.ChoiceField(
        required = False,
        label = _(u'Access type'),
    )
    
    closed = forms.BooleanField(
        required = False,
        label = _(u'Closed'),
        initial = False
    )
    
    important = forms.BooleanField(
        required = False,
        label = _(u'Important'),
        initial = False
    )
    
    voting = forms.BooleanField(
        required = False,
        label = _(u'Voting'),
        initial = False
    )
    
    def __init__(self, models, thread, comment, voting, moderate, *args, **kwargs):
        self.base_fields['access_type'].choices = models.THREAD_ACCESS_TYPE_CHOICES
        self.base_fields['access_type'].initial = models.THREAD_ACCESS_TYPE_NOT_SET
        if not thread:
            self.caption = _('add thread')
            self.base_fields['title'].initial = ''
            self.base_fields['body'].initial = ''
            self.base_fields['closed'].initial = False
            self.base_fields['important'].initial = False
        else:
            self.caption = _('edit thread')
            self.base_fields['title'].initial = thread.title
            self.base_fields['body'].initial = thread.body
            self.base_fields['access_type'].initial = thread.access_type
            self.base_fields['closed'].initial = thread.closed
            self.base_fields['important'].initial = thread.important
        if comment:
            self.base_fields['voting'].initial = comment.voting
            self.base_fields['body'].initial = comment.body
        if not thread:
            self.base_fields['closed'].widget = forms.HiddenInput()
            self.base_fields['closed'].is_hidden = True
        else:
            self.base_fields['closed'].widget = forms.CheckboxInput()
            self.base_fields['closed'].is_hidden = False    
        if not voting:
            self.base_fields['voting'].widget = forms.HiddenInput()            
            self.base_fields['voting'].is_hidden = True
        else:
            self.base_fields['voting'].widget = forms.CheckboxInput()
            self.base_fields['voting'].is_hidden = False    
        if not moderate:
            self.base_fields['important'].widget = forms.HiddenInput()
            self.base_fields['important'].is_hidden = True
        else:
            self.base_fields['important'].widget = forms.CheckboxInput()
            self.base_fields['important'].is_hidden = False    
        super(ThreadForm, self).__init__(*args, **kwargs)
        