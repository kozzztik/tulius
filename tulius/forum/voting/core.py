from djfw.inlineformsets import get_formset
# TODO: fix this when module moved
from tulius.forum.plugins import ForumPlugin, BasePluginView
from .forms import DeleteVotingForm, VoitingForm, VoitingChoiceForm, ManageForm


class VotingCore(ForumPlugin):
    def prepare_voting_results(self, voting, view_user, force_results=False):
        models = self.site.core.models
        if view_user and not view_user.is_anonymous:
            votes = models.VotingVote.objects.filter(
                user=view_user, choice__voting=voting)
            voting.choice = votes[0].choice if votes else None
            if voting.choice and voting.show_results:
                force_results = True        
        if voting.closed or force_results:
            choices = models.VotingChoice.objects.filter(voting=voting)
            votes = 0
            for choice in choices:
                choice.vote_count = models.VotingVote.objects.filter(
                    choice=choice).count()
                votes += choice.vote_count
            for choice in choices:
                choice.vote_persent = (
                        choice.vote_count * 100 / votes) if votes else 0
                choice.vote_length = choice.vote_persent / 2
                if choice.vote_length < 1:
                    choice.vote_length = 1
            voting.finished_choices = choices

    def preprocess_add_voting(self, request):
        models = self.site.core.models
        form = VoitingForm(data=request.POST or None)
        formset = get_formset(
            models.Voting,
            models.VotingChoice,
            request.POST,
            VoitingChoiceForm,
            extra=2)
        valid = False
        if request.method == 'POST':
            valid = form.is_valid() and formset.is_valid()
        return valid, form, formset
    
    def process_add_voting(self, form, formset, comment, user):
        voting = form.save(commit=False)
        voting.comment = comment
        voting.user = user
        voting.save()
        for form in formset:
            voting_choice = form.save(commit=False)
            voting_choice.voting = voting
            voting_choice.save()
        return voting
    
    def preprocess_edit_voting(self, request, comment):
        models = self.site.core.models
        votings = models.Voting.objects.filter(comment=comment)
        if votings.count() > 0:
            voting = votings[0]
        else:
            voting = None
        if voting:
            if voting.closed:
                voting_delete = DeleteVotingForm(data=request.POST or None)
            else:
                voting_delete = ManageForm(data=request.POST or None)
            voting_form = None
            voting_formset = None
        else:
            voting_delete = None
            voting_form = VoitingForm(data=request.POST or None)
            voting_formset = get_formset(
                models.Voting,
                models.VotingChoice,
                request.POST,
                VoitingChoiceForm,
                extra=2)
        valid = False
        if request.method == 'POST':
            if voting:
                valid = voting_delete.is_valid()
                if valid:
                    if not voting.closed:
                        voting.do_close = voting_delete.cleaned_data[
                            'close_voting']
                    else:
                        voting.do_close = False
                    voting.do_delete = voting_delete.cleaned_data[
                        'delete_voting']
                    
            else:
                valid = voting_form.is_valid() and voting_formset.is_valid()
                
        else:
            if voting:
                self.prepare_voting_results(voting, request.user, True)
        return valid, voting, voting_form, voting_formset, voting_delete
    
    def process_edit_voting(self, voting, form, formset, comment, user):
        if voting:
            if voting.do_delete:
                self.delete_voting(voting)
            else:
                if voting.do_close:
                    voting.closed = True
                    voting.save()
        else:
            self.process_add_voting(form, formset, comment, user)
            
    def delete_voting(self, voting):
        models = self.site.core.models
        voting_choices = models.VotingChoice.objects.filter(voting=voting)
        for voting_choice in voting_choices:
            voices = models.VotingVote.objects.filter(choice=voting_choice)
            voices.delete()
        voting_choices.delete()
        voting.delete()
        
    def delete_votings(self, category, comment):
        models = self.site.core.models
        votings = models.Voting.objects.filter(comment=comment)
        for voting in votings:
            self.delete_voting(voting)
    
    def thread_before_edit(self, sender, **kwargs):
        context = kwargs['context']
        context['show_voting'] = not sender.self_is_room
        if sender.self_is_room:
            return
        thread = kwargs['thread']
        voting = None
        if thread and thread.first_comment:
            first_comment = self.models.Comment.objects.get(
                id=thread.first_comment_id)
            (voting_valid, voting, voting_form, voting_formset,
             voting_delete) = self.preprocess_edit_voting(
                sender.request, first_comment)
            context['voting_delete'] = voting_delete
        else:
            (voting_valid, voting_form, voting_formset) = \
                self.preprocess_add_voting(sender.request)
        sender.voting = voting
        sender.voting_form = voting_form
        sender.voting_formset = voting_formset
        context['voting'] = voting
        context['voting_form'] = voting_form
        context['voting_formset'] = voting_formset
        if not voting_valid:
            sender.edit_is_valid = False

    def thread_after_edit(self, sender, **kwargs):
        if sender.self_is_room or (not sender.request.POST):
            return
        if sender.comment and sender.comment.voting:
            self.process_edit_voting(
                sender.voting,
                sender.voting_form,
                sender.voting_formset,
                sender.comment,
                sender.request.user)
    
    def comment_before_edit(self, sender, **kwargs):
        voting = None
        comment = kwargs['comment']
        context = kwargs['context']
        if comment:
            (voting_valid, voting, voting_form, voting_formset,
             voting_delete) = self.preprocess_edit_voting(
                sender.request, comment)
            context['voting_delete'] = voting_delete
        else:
            (voting_valid, voting_form, voting_formset) = \
                self.preprocess_add_voting(sender.request)
        context['voting_valid'] = voting_valid
        context['voting'] = voting
        context['voting_form'] = voting_form
        context['voting_formset'] = voting_formset
        if not voting_valid:
            sender.edit_is_valid = False
            
    def comment_after_edit(self, sender, **kwargs):
        if sender.request.POST and sender.comment and sender.comment.voting:
            context = kwargs['context']
            voting = context['voting']
            voting_form = context['voting_form']
            voting_formset = context['voting_formset']
            self.process_edit_voting(
                voting,
                voting_form,
                voting_formset,
                sender.comment,
                sender.request.user)
    
    def init_core(self):
        super(VotingCore, self).init_core()
        self.core['preprocess_add_voting'] = self.preprocess_add_voting
        self.core['process_add_voting'] = self.process_add_voting
        self.core['preprocess_edit_voting'] = self.preprocess_edit_voting
        self.core['process_edit_voting'] = self.process_edit_voting
        self.core['delete_voting'] = self.delete_voting
        self.core['delete_votings'] = self.delete_votings
        self.core['prepare_voting_results'] = self.prepare_voting_results
        self.site.signals.thread_before_edit.connect(self.thread_before_edit)
        self.site.signals.thread_after_edit.connect(self.thread_after_edit)
        self.site.signals.comment_before_edit.connect(self.comment_before_edit)
        self.site.signals.comment_after_edit.connect(self.comment_after_edit)
