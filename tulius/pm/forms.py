from django import forms

from tulius.pm import models


class PrivateMessageForm(forms.ModelForm):

    class Meta:
        model = models.PrivateMessage
        fields = ('body',)

    def __init__(self, sender, receiver, *args, **kwargs):
        self.sender = sender
        self.receiver = receiver
        super(PrivateMessageForm, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        pm = super(PrivateMessageForm, self).save(commit=False)
        pm.receiver = self.receiver
        pm.sender = self.sender
        pm.save()
        return pm
