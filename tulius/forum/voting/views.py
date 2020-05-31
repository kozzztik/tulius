import json

from django import http
from django import shortcuts
from django.core import exceptions
from django.utils import html
from django.db import models as django_models
from tulius.forum import plugins
from tulius.forum import models


class Like(plugins.BasePluginView):
    """
    Mark post as liked
    """
    require_user = True

    def get(self, request, *args, **kwargs):
        if request.user.is_anonymous:
            raise http.Http404()
        comment_id = request.GET['postid']
        value = request.GET['value'] == 'true'
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

    def get(self, request, *args, **kwargs):
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
            votes.delete()
        vote = models.VotingVote(user=request.user, choice=choice)
        vote.save()
        self.voting = choice.voting
        ret_json = {'success': True, 'html':  self.render()}
        return http.HttpResponse(json.dumps(ret_json))


class PreviewResults(BaseVoting):
    require_user = True
    force_results = True

    def get(self, request, *args, **kwargs):
        voting_id = int(request.GET['voting_id'])
        self.voting = shortcuts.get_object_or_404(models.Voting, id=voting_id)
        parent_comment = self.voting.comment
        parent_thread = parent_comment.parent
        parent_thread.view_user = request.user
        if not parent_thread.read_right:
            raise http.Http404()
        ret_json = {'success': True, 'html':  self.render()}
        return http.HttpResponse(json.dumps(ret_json))


class VotingAPI(plugins.BaseAPIView):
    obj = None
    no_revote = False

    def choice_json(self):
        choice = self.obj.user_choice(self.user)
        if not choice:
            return None
        return {
            'id': choice.pk,
            'name': html.escape(choice.name),
        }

    def choices_json(self, user_choice):
        force_results = bool(
            self.obj.closed or (user_choice and self.obj.show_results))
        choices = models.VotingChoice.objects.filter(
            voting=self.obj).annotate(
                count=django_models.Count('voting_choices'))
        items = []
        votes = 0
        include_results = force_results or self.obj.preview_results
        for choice in choices:
            items.append({
                'id': choice.pk,
                'name': html.escape(choice.name),
                'count': choice.count if include_results else None,
            })
            votes += choice.count
        if include_results:
            for item in items:
                item['percent'] = (item['count'] * 100 / votes) if votes else 0
        return {
            'with_results': force_results,
            'items': items,
            'votes': votes,
        }

    def voting_json(self):
        choice = self.choice_json()
        return {
            'id': self.obj.pk,
            'name': html.escape(self.obj.voting_name),
            'body': html.escape(self.obj.voting_body),
            'closed': self.obj.closed,
            'anonymous': self.obj.anonymous,
            'show_results': self.obj.show_results,
            'preview_results': self.obj.preview_results,
            'choice': choice,
            'choices': self.choices_json(choice),
        }

    def get_context_data(self, **kwargs):
        comment_id = int(kwargs['pk'])
        comment = shortcuts.get_object_or_404(models.Comment, id=comment_id)
        thread = comment.parent
        thread.view_right = self.user  # TODO oooh
        if not thread.read_right:
            raise exceptions.PermissionDenied()
        self.obj = shortcuts.get_object_or_404(models.Voting, comment=comment)

    def get(self, request, *args, **kwargs):
        self.get_context_data(**kwargs)
        return self.voting_json()

    def post(self, request, *args, **kwargs):
        self.get_context_data(**kwargs)
        data = json.loads(self.request.body)
        choice_id = int(data['choice'])
        choice = shortcuts.get_object_or_404(
            models.VotingChoice, pk=choice_id)
        if choice.voting_id != self.obj.pk:
            raise http.Http404()
        votes = models.VotingVote.objects.filter(
            choice__voting=self.obj, user=request.user)
        if votes:
            if self.no_revote:
                raise http.Http404()
            votes.delete()
        models.VotingVote(user=request.user, choice=choice).save()
        return self.voting_json()
