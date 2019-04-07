from django.conf import urls

from tulius.forum.voting import core
from tulius.forum.voting import views



class VotingPlugin(core.VotingCore):
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
        likes = self.models.CommentLike.objects.filter(
            comment=comment, user=comment.view_user)
        return bool(likes)

    def init_core(self):
        super(VotingPlugin, self).init_core()
        self.templates['voting_closed_results'] = \
            'forum/voting/closed_results.haml'
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
        return [
            urls.url(r'^like/$', views.Like.as_view(plugin=self), name='like'),
            urls.url(r'^vote/$', views.Vote.as_view(plugin=self), name='vote'),
            urls.url(
                r'^preview_results/$',
                views.PreviewResults.as_view(plugin=self),
                name='preview_results'),
        ]
