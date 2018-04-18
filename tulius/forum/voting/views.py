import json

from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponse

from .core import BasePluginView


class Like(BasePluginView):
    """
    Mark post as liked
    """
    require_user = True
    
    def get(self, request):
        if request.user.is_anonymous:
            raise Http404()
        comment_id = request.GET['postid']
        value = request.GET['value'] == 'true'
        models = self.core.models
        try:
            comment_id = int(comment_id)
        except:
            raise Http404()
        comment = get_object_or_404(models.Comment, id=comment_id)

        if not comment.parent.read_right(request.user):
            ret_json = {'success': False, 'value': value}
            return HttpResponse(json.dumps(ret_json))
        
        like_marks = models.CommentLike.objects.filter(
            user=request.user, comment=comment)
        like_count = comment.likes
        if like_marks:
            for like in like_marks:
                like.delete()
            like_count -= 1
            value = False
        else:
            if len(like_marks) == 0:
                like_mark = models.CommentLike(
                    user=request.user, comment=comment)
                like_mark.save()
            like_count += 1
            value = True
        ret_json = {
            'success': True,
            'value': value,
            'like_count': like_count,
            'comment_id': comment_id}
        return HttpResponse(json.dumps(ret_json))


class BaseVoting(BasePluginView):
    template_name = 'voting'
    force_results = False

    def get_context_data(self, **kwargs):
        context = BasePluginView.get_context_data(self, **kwargs)
        context['voting'] = self.voting
        self.core.prepare_voting_results(
            self.voting, self.request.user, self.force_results)
        return context
        

class Vote(BaseVoting):
    require_user = True
    no_revote = False
    
    def get(self, request):
        models = self.core.models
        choice_id = int(request.GET['choice_id'])
        choice = get_object_or_404(models.VotingChoice, id=choice_id)
        voting = choice.voting
        parent_comment = voting.comment
        if not parent_comment.parent.read_right(request.user):
            raise Http404()
        votes = models.VotingVote.objects.filter(
            choice=choice, user=request.user)
        if votes:
            if self.no_revote:
                raise Http404()
            else:
                votes.delete()
        vote = models.VotingVote(user=request.user, choice=choice)
        vote.save()
        self.voting = choice.voting
        ret_json = {'success': True, 'html':  self.render()}
        return HttpResponse(json.dumps(ret_json))


class PreviewResults(BaseVoting):
    require_user = True
    force_results = True
    
    def get(self, request):
        models = self.core.models
        voting_id = int(request.GET['voting_id'])
        self.voting = get_object_or_404(models.Voting, id=voting_id)
        parent_comment = self.voting.comment
        parent_thread = parent_comment.parent
        parent_thread.view_user = request.user
        if not parent_thread.read_right:
            raise Http404()
        ret_json = {'success': True, 'html':  self.render()}
        return HttpResponse(json.dumps(ret_json))
