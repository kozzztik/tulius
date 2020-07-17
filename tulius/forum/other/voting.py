import json

from django import http
from django import dispatch
from django import shortcuts
from django.core import exceptions
from django.db import models as django_models
from django.db import transaction
from django.utils import html

from tulius.core.ckeditor import html_converter
from tulius.forum import models
from tulius.forum import signals
from tulius.forum.comments import signals as comment_signals
from tulius.forum.comments import api
from djfw.wysibb.templatetags import bbcodes


@dispatch.receiver(signals.comment_to_json)
def comment_to_json(sender, comment, data, **kwargs):
    # TODO better to store data directly in media, avoiding loading of it,
    # TODO but it is too much changes at one time to get rid of it while
    # TODO previous implementation is still in place
    pk = comment.media.get('voting')
    if not pk or isinstance(pk, dict):
        return
    voting = models.Voting.objects.filter(pk=pk).first()
    if not voting:
        comment.media['voting'] = None
        return
    data['media']['voting'] = VotingAPI.voting_json(voting, sender.user)


@dispatch.receiver(signals.thread_view)
def thread_view(sender, response, **kwargs):
    pk = sender.obj.media.get('voting')
    if not pk or isinstance(pk, dict):
        return
    voting = models.Voting.objects.filter(pk=pk).first()
    if not voting:
        response['media']['voting'] = None
        return
    response['media']['voting'] = VotingAPI.voting_json(voting, sender.user)


@dispatch.receiver(comment_signals.after_add)
def after_add_comment(sender, comment, data, preview, view, **kwargs):
    voting_data = data['media'].get('voting')
    if not voting_data:
        return
    if preview:
        comment.media['voting'] = voting_data
        if not view.obj.pk:
            view.obj.media['voting'] = voting_data
        return
    voting = VotingAPI.create_voting(comment, view.user, voting_data)
    comment.media['voting'] = voting.pk
    comment.save()
    if comment.id == view.obj.first_comment_id:
        view.obj.media['voting'] = voting.pk
        view.obj.save()


@dispatch.receiver(signals.on_comment_update)
def on_comment_update(sender, comment, data, preview, **kwargs):
    voting_data = data['media'].get('voting')
    if not voting_data:
        return
    orig_data = comment.media.get('voting')
    if preview:
        comment.media['voting'] = voting_data
        if sender.obj.first_comment_id == comment.id:
            sender.obj.media['voting'] = voting_data
        return
    if not orig_data:
        # voting added
        voting = VotingAPI.create_voting(comment, sender.user, voting_data)
        comment.media['voting'] = voting.pk
        if sender.obj.first_comment_id == comment.id:
            sender.obj.media['voting'] = voting.pk
        return
    voting = models.Voting.objects.filter(pk=orig_data).first()
    if not voting:
        return
    voting.voting_name = html_converter.html_to_bb(voting_data['name'])
    voting.voting_body = html_converter.html_to_bb(voting_data['body'])
    voting.show_results = voting_data['show_results']
    voting.preview_results = voting_data['preview_results']
    voting.save()


class VotingAPI(api.CommentBase):
    voting = None

    @classmethod
    def choice_json(cls, voting, user):
        choice = voting.user_choice(user)
        if not choice:
            return None
        return {
            'id': choice.pk,
            'name': html.escape(choice.name),
        }

    @classmethod
    def choices_json(cls, voting, user_choice):
        force_results = bool(
            voting.closed or (user_choice and voting.show_results))
        choices = models.VotingChoice.objects.filter(
            voting=voting).annotate(
                count=django_models.Count('voting_choices'))
        items = []
        votes = 0
        include_results = force_results or voting.preview_results
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

    @classmethod
    def voting_json(cls, voting, user):
        choice = cls.choice_json(voting, user)
        return {
            'id': voting.pk,
            'name': bbcodes.bbcode(voting.voting_name),
            'body': bbcodes.bbcode(voting.voting_body),
            'closed': voting.closed,
            'anonymous': voting.anonymous,
            'show_results': voting.show_results,
            'preview_results': voting.preview_results,
            'choice': choice,
            'choices': cls.choices_json(voting, choice),
        }

    def get_voting(self, **kwargs):
        self.get_comment(**kwargs)
        pk = self.comment.media.get('voting')
        if not pk:
            raise http.Http404()
        self.voting = shortcuts.get_object_or_404(models.Voting, pk=pk)

    @classmethod
    def create_voting(cls, comment, user, data):
        voting = models.Voting(
            comment=comment, user=user,
            voting_name=html_converter.html_to_bb(data['name']),
            voting_body=html_converter.html_to_bb(data['body']),
            show_results=data['show_results'],
            preview_results=data['preview_results'],
        )
        voting.save()
        for item in data['choices']['items']:
            models.VotingChoice(
                voting=voting, name=html_converter.html_to_bb(item['name'])
            ).save()
        return voting

    def get_context_data(self, **kwargs):
        self.get_voting(**kwargs)
        return self.voting_json(self.voting, self.user)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        self.get_voting(**kwargs)
        data = json.loads(self.request.body)
        if data.get('close'):
            if not self.comment_edit_right(self.comment):
                raise exceptions.PermissionDenied()
            self.voting.closed = True
            self.voting.save()
            return self.voting_json(self.voting, self.user)
        choice_id = int(data['choice'])
        choice = shortcuts.get_object_or_404(
            models.VotingChoice, pk=choice_id)
        if choice.voting_id != self.voting.pk:
            raise http.Http404()
        votes = models.VotingVote.objects.filter(
            choice__voting=self.voting, user=request.user)
        if votes:
            raise http.Http404()
        models.VotingVote(user=request.user, choice=choice).save()
        return self.voting_json(self.voting, self.user)
