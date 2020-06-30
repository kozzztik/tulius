from tulius.forum import plugins


class VotingCore(plugins.ForumPlugin):
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

    def init_core(self):
        super(VotingCore, self).init_core()
        self.core['delete_voting'] = self.delete_voting
        self.core['delete_votings'] = self.delete_votings
        self.core['prepare_voting_results'] = self.prepare_voting_results
