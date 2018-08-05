import json

from django import http
from django import shortcuts

from tulius.forum import plugins


class Like(plugins.BasePluginView):
    """
    Mark post as liked
    """
    require_user = True

    def get(self, request):
        if request.user.is_anonymous:
            raise http.Http404()
        comment_id = request.GET['postid']
        value = request.GET['value'] == 'true'
        models = self.core.models
        try:
            comment_id = int(comment_id)
        except:
            raise http.Http404()
        comment = shortcuts.get_object_or_404(models.Comment, id=comment_id)

        if not comment.parent.read_right(request.user):
            ret_json = {'success': False, 'value': value}
            return http.HttpResponse(json.dumps(ret_json))

        like_marks = models.CommentLike.objects.filter(
            user=request.user, comment=comment)
        like_count = comment.likes
        if like_marks:
            for like in like_marks:
                like.delete()
            like_count -= 1
            value = False
        else:
            if not like_marks:
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
        return http.HttpResponse(json.dumps(ret_json))


class BaseVoting(plugins.BasePluginView):
    template_name = 'voting'
    force_results = False

    def get_context_data(self, **kwargs):
        context = plugins.BasePluginView.get_context_data(self, **kwargs)
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
        choice = shortcuts.get_object_or_404(models.VotingChoice, id=choice_id)
        voting = choice.voting
        parent_comment = voting.comment
        if not parent_comment.parent.read_right(request.user):
            raise http.Http404()
        votes = models.VotingVote.objects.filter(
            choice=choice, user=request.user)
        if votes:
            if self.no_revote:
                raise http.Http404()
            else:
                votes.delete()
        vote = models.VotingVote(user=request.user, choice=choice)
        vote.save()
        self.voting = choice.voting
        ret_json = {'success': True, 'html':  self.render()}
        return http.HttpResponse(json.dumps(ret_json))


class PreviewResults(BaseVoting):
    require_user = True
    force_results = True

    def get(self, request):
        models = self.core.models
        voting_id = int(request.GET['voting_id'])
        self.voting = shortcuts.get_object_or_404(models.Voting, id=voting_id)
        parent_comment = self.voting.comment
        parent_thread = parent_comment.parent
        parent_thread.view_user = request.user
        if not parent_thread.read_right:
            raise http.Http404()
        ret_json = {'success': True, 'html':  self.render()}
        return http.HttpResponse(json.dumps(ret_json))
