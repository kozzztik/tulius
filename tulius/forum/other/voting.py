import json

from django import http
from django import dispatch
from django.core import exceptions
from django.db import transaction
from django.utils import html

from tulius.core.ckeditor import html_converter
from tulius.forum import models
from tulius.forum.threads import signals as thread_signals
from tulius.forum.comments import signals as comment_signals
from tulius.forum.comments import views
from djfw.wysibb.templatetags import bbcodes


def create_voting(data):
    return {
        'name': bbcodes.bbcode(html_converter.html_to_bb(data['name'])),
        'body': bbcodes.bbcode(html_converter.html_to_bb(data['body'])),
        'closed': False,
        'show_results': bool(data['show_results']),
        'preview_results': bool(data['preview_results']),
        'choices': {
            'items': [{
                'id': i,
                'name': html.escape(item['name']),
                'count': 0,
                'percent': 0,
            } for i, item in enumerate(data['choices']['items'])],
            'votes': 0,
        },
    }


class VotingAPI(views.CommentBase):
    voting_model = models.VotingVote

    def get_voting(self, for_update=False, **kwargs):
        self.get_comment(for_update=for_update, **kwargs)
        voting = self.comment.media.get('voting')
        if not voting:
            raise http.Http404()
        return voting

    def get_context_data(self, **kwargs):
        return self.get_voting(**kwargs)

    @transaction.atomic
    def post(self, request, **kwargs):
        voting = self.get_voting(for_update=True, **kwargs)
        data = json.loads(self.request.body)
        if data.get('close'):
            if not self.comment_edit_right(self.comment):
                raise exceptions.PermissionDenied()
            voting['closed'] = True
            self.comment.save()
            return self.user_voting_data(voting, self.user, self.comment.pk)
        choice = int(data['choice'])
        if (choice < 0) or (choice >= len(voting['choices']['items'])):
            raise exceptions.ValidationError('Invalid choice')
        votes = self.voting_model.objects.filter(
            comment=self.comment, user=request.user)
        if votes:
            raise http.Http404()
        self.voting_model(
            user=request.user, choice=choice, comment=self.comment).save()
        voting['choices']['items'][choice]['count'] += 1
        voting['choices']['votes'] += 1
        count = voting['choices']['votes']
        for item in voting['choices']['items']:
            item['percent'] = item['count'] * 100 / count
        self.comment.save()
        return self.user_voting_data(voting, self.user, self.comment.pk)

    @classmethod
    def user_choice(cls, choices, user, comment_id):
        if user.is_anonymous:
            return None
        choice = cls.voting_model.objects.filter(
            user=user, comment_id=comment_id).first()
        if not choice:
            return None
        return {
            'id': choice.choice,
            'name': html.escape(choices['items'][choice.choice]['name']),
        }

    @classmethod
    def user_voting_data(cls, data, user, comment_id):
        data['id'] = comment_id  # backward compatibility with frontend
        data['choice'] = cls.user_choice(data['choices'], user, comment_id)
        with_results = bool(
            data['closed'] or
            data['preview_results'] or
            (data['choice'] and data['show_results']))
        if not with_results:
            for item in data['choices']['items']:
                item['count'] = None
                del item['percent']
        data['choices']['with_results'] = bool(
            data['closed'] or (data['choice'] and data['show_results']))
        return data

    @classmethod
    def on_comment_to_json(cls, _, comment, data, view, **_kwargs):
        v = comment.media.get('voting')
        if v:
            data['media']['voting'] = cls.user_voting_data(
                v, view.user, comment.pk)

    @classmethod
    def on_thread_to_json(cls, instance, response, view, **_kwargs):
        v = instance.media.get('voting')
        if v:
            response['media']['voting'] = cls.user_voting_data(
                v, view.user, instance.first_comment_id)

    @classmethod
    def on_before_add_comment(cls, _, comment, data, view, **_kwargs):
        voting_data = data['media'].get('voting')
        if not voting_data:
            return
        voting = create_voting(voting_data)
        comment.media['voting'] = voting
        if (not view.obj.pk) or (comment.id == view.obj.first_comment_id):
            view.obj.media['voting'] = voting

    @classmethod
    def on_comment_update(cls, _, comment, data, view, **_kwargs):
        voting_data = data['media'].get('voting')
        if not voting_data:
            return
        orig_data = comment.media.get('voting')
        if not orig_data:
            voting = create_voting(voting_data)
            comment.media['voting'] = voting
            if view.obj.first_comment_id == comment.id:
                view.obj.media['voting'] = voting
            return
        orig_data['name'] = html_converter.html_to_bb(voting_data['name'])
        orig_data['body'] = html_converter.html_to_bb(voting_data['body'])
        orig_data['show_results'] = bool(voting_data['show_results'])
        orig_data['preview_results'] = voting_data['preview_results']
        if comment.id == view.obj.first_comment_id:
            view.obj.media['voting'] = orig_data


@dispatch.receiver(comment_signals.to_json)
def tmp_comment_to_json_plugin_filter(sender, comment, data, view, **kwargs):
    # TODO this func will be removed with plugin_id field cleanup
    # it will use signals "sender" field
    if view.obj.plugin_id:
        return None
    return VotingAPI.on_comment_to_json(sender, comment, data, view, **kwargs)


@dispatch.receiver(thread_signals.to_json)
def tmp_thread_view_plugin_filter(instance, response, view, **kwargs):
    # TODO this func will be removed with plugin_id field cleanup
    # it will use signals "sender" field
    if instance.plugin_id:
        return None
    return VotingAPI.on_thread_to_json(instance, response, view, **kwargs)


@dispatch.receiver(comment_signals.before_add)
def tmp_on_before_add_comment_plugin_filter(
        sender, comment, data, view, **kwargs):
    # TODO this func will be removed with plugin_id field cleanup
    # it will use signals "sender" field
    if view.obj.plugin_id:
        return None
    return VotingAPI.on_before_add_comment(
        sender, comment, data, view, **kwargs)


@dispatch.receiver(comment_signals.on_update)
def tmp_on_comment_update_plugin_filter(sender, comment, data, view, **kwargs):
    # TODO this func will be removed with plugin_id field cleanup
    # it will use signals "sender" field
    if view.obj.plugin_id:
        return None
    return VotingAPI.on_comment_update(sender, comment, data, view, **kwargs)
