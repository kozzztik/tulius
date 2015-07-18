from django.conf.urls import patterns, url
from .views import Like, Vote, PreviewResults

from .core import VotingCore

class VotingPlugin(VotingCore):
    def comment_voting(self, comment):
        votings = self.models.Voting.objects.filter(comment=comment)
        if not votings:
            return None
        voting = votings[0]
        self.prepare_voting_results(voting, comment.view_user)
        return voting
    
    def like_url(self):
        return self.reverse('like')
    
    def vote_url(self):
        return self.reverse('vote')
    
    def preview_url(self):
        return self.reverse('preview_results')
    
    def is_liked(self, comment):
        likes = self.models.CommentLike.objects.filter(comment=comment, user=comment.view_user)
        return True if likes else False
    
    def init_core(self):
        super(VotingPlugin, self).init_core()
        self.templates['voting_closed_results'] = 'forum/voting/closed_results.haml'
        self.templates['voting_results'] = 'forum/voting/voting_results.haml'
        self.templates['voting'] = 'forum/voting/voting.haml'
        self.templates['voting_tag'] = 'forum/voting/voting_tag.haml'
        self.templates['voting_tag'] = 'forum/voting/voting_tag.haml'
        self.core['Comment_voting_obj'] = self.comment_voting
        self.core['Comment_is_liked'] = self.is_liked
        self.urlizer['vote'] = self.vote_url
        self.urlizer['like'] = self.like_url
        self.urlizer['voting_preview'] = self.preview_url
        self.urlizer['Thread_get_voting_url'] = self.vote_url
        
    def get_urls(self):
        return patterns('',
            url(r'^like/$', Like.as_view(plugin=self), name='like'),
            url(r'^vote/$', Vote.as_view(plugin=self), name='vote'),
            url(r'^preview_results/$', PreviewResults.as_view(plugin=self), name='preview_results'),
        )