from django.utils.translation import ugettext_lazy as _
from django import forms

class CommentForm(forms.Form):
    """
    Add/edit forum comment form
    """
    title = forms.CharField(
        required = False,
        label = _(u'Title'),
    )
    
    body = forms.CharField(
        required = False,
        label = _(u'Body'),
        widget=forms.widgets.Textarea(),
    )
    voting = forms.BooleanField(
        required = False,
        label = _(u'voting'),
    )
    def __init__(self, voting_enabled, *args, **kwargs):
        super(CommentForm, self).__init__(*args,  **kwargs)
        if not voting_enabled:
            self.fields['voting'].widget = forms.widgets.HiddenInput(),
            
class CommentDeleteForm(forms.Form):
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