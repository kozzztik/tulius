from django import dispatch

from tulius.forum import models as forum_models
from tulius.forum.comments import signals as comment_signals
from tulius.forum.threads import signals as thread_signals
from tulius.forum.other import voting
from tulius.forum.other import readmarks
from tulius.forum.other import likes
from tulius.forum.other import search
from tulius.gameforum import base
from tulius.gameforum import consts
from tulius.gameforum.threads import views as thread_views
from tulius.gameforum.comments import views as comments_api
from tulius.stories import models as story_models


class ReadmarkAPI(readmarks.ReadmarkAPI, thread_views.BaseThreadAPI):
    read_mark_model = forum_models.ThreadReadMark
    comment_model = forum_models.Comment


@dispatch.receiver(comment_signals.on_delete)
def tmp_on_comment_delete_plugin_filter(sender, comment, view, **kwargs):
    # TODO this func will be removed with plugin_id field cleanup
    # it will use signals "sender" field
    if comment.plugin_id != consts.GAME_FORUM_SITE_ID:
        return None
    return ReadmarkAPI.on_delete_comment(sender, comment, view, **kwargs)


@dispatch.receiver(comment_signals.after_add)
def tmp_on_after_add_comment_plugin_filter(comment, preview, view, **kwargs):
    # TODO this func will be removed with plugin_id field cleanup
    # it will use signals "sender" field
    if comment.plugin_id != consts.GAME_FORUM_SITE_ID:
        return None
    return ReadmarkAPI.after_add_comment(comment, preview, view, **kwargs)


@dispatch.receiver(thread_signals.prepare_room)
def tmp_on_prepare_room_plugin_filter(room, threads, view, **_kwargs):
    # TODO this func will be removed with plugin_id field cleanup
    # it will use signals "sender" field
    if room.plugin_id != consts.GAME_FORUM_SITE_ID:
        return None
    return ReadmarkAPI.on_prepare_room_list(room, threads, view, **_kwargs)


@dispatch.receiver(thread_signals.prepare_threads)
def tmp_on_prepare_threads_plugin_filter(threads, view, **kwargs):
    # TODO this func will be removed with plugin_id field cleanup
    # it will use signals "sender" field
    if view.plugin_id != consts.GAME_FORUM_SITE_ID:
        return None
    return ReadmarkAPI.on_thread_prepare_thread(threads, view, **kwargs)


@dispatch.receiver(thread_signals.to_json)
def tmp_on_thread_to_json_plugin_filter(instance, view, response, **kwargs):
    # TODO this func will be removed with plugin_id field cleanup
    # it will use signals "sender" field
    if instance.plugin_id != consts.GAME_FORUM_SITE_ID:
        return None
    return ReadmarkAPI.on_thread_to_json(instance, view, response, **kwargs)


class VotingAPI(voting.VotingAPI, comments_api.CommentsBase):
    voting_model = forum_models.VotingVote


class Search(search.Search, base.VariationMixin):
    comments_class = comments_api.CommentAPI

    def get_view(self, comment):
        view = super(Search, self).get_view(comment)
        view.variation = self.variation
        return view

    def apply_users_filters(self, comments, conditions, data):
        filter_users = data.get('users', [])
        filter_not_users = data.get('not_users', [])
        if filter_users:
            users = story_models.Role.objects.filter(
                pk__in=filter_users, variation=self.variation)
            conditions.append('От: ' + ', '.join([u.name for u in users]))
            comments = comments.filter(data1__in=[u.pk for u in users])
        if filter_not_users:
            users = story_models.Role.objects.filter(
                pk__in=filter_not_users, variation=self.variation)
            conditions.append(
                'Не от: ' + ', '.join([u.name for u in users]))
            comments = comments.exclude(data1__in=[u.pk for u in users])
        return comments


class Favorites(likes.Favorites):
    comments_class = comments_api.CommentAPI
    variations = None

    def get_view(self, comment):
        view = super(Favorites, self).get_view(comment)
        tree_id = view.comment.parent.tree_id
        self.variations = self.variations or {}
        if tree_id not in self.variations:
            variation = story_models.Variation.objects.get(
                thread__tree_id=tree_id)
            self.variations[tree_id] = variation
        view.variation = self.variations[tree_id]
        return view

    @staticmethod
    def comments_to_json(view_objects):
        variations = {}
        for api in view_objects:
            variations.setdefault(api.variation, [])
            variations[api.variation].append(api)
        return {
            'groups': [{
                'name': variation.name,
                'variation_id': variation.pk,
                'items':  [{
                    'comment': api.comment_to_json(api.comment),
                    'thread': api.obj_to_json(),
                } for api in items]
            } for variation, items in variations.items()]
        }
