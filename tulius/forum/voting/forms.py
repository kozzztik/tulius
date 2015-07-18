from django.utils.translation import ugettext_lazy as _
from django import forms
#TODO: ITS BAD, but i have no time to fix it, and all this must be refactored soon
from tulius.forum.models import Voting, VotingChoice

class DeleteVotingForm(forms.Form):
    delete_voting = forms.BooleanField(label=_("Delete voting"), required=False)
    
class ManageForm(DeleteVotingForm):
    close_voting = forms.BooleanField(label=_("Close voting"), required=False)
    
class VoitingForm(forms.models.ModelForm):
    class Meta:
        model = Voting
        fields = ('voting_name', 'voting_body', 'show_results', 'preview_results')
        
class VoitingChoiceForm(forms.models.ModelForm):
    class Meta:
        model = VotingChoice
        

