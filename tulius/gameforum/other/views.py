from tulius.forum.comments import signals as comment_signals
from tulius.forum.threads import signals as thread_signals
from tulius.forum.other import voting
from tulius.forum.other import readmarks
from tulius.forum.other import likes
from tulius.forum.other import search
from tulius.gameforum import base
from tulius.gameforum.threads import views as thread_views
from tulius.gameforum.threads import models as thread_models
from tulius.gameforum.comments import views as comments_api
from tulius.gameforum.comments import models as comment_models
from tulius.gameforum.other import models as other_models
from tulius.stories import models as story_models


class ReadmarkAPI(readmarks.ReadmarkAPI, thread_views.BaseThreadAPI):
    read_mark_model = other_models.ThreadReadMark
    comment_model = comment_models.Comment


comment_signals.on_delete.connect(
    ReadmarkAPI.on_delete_comment, sender=comment_models.Comment)
comment_signals.after_add.connect(
    ReadmarkAPI.after_add_comment, sender=comment_models.Comment)
thread_signals.prepare_room.connect(
    ReadmarkAPI.on_prepare_room_list, sender=thread_models.Thread)
thread_signals.prepare_threads.connect(
    ReadmarkAPI.on_thread_prepare_thread, sender=thread_models.Thread)
thread_signals.to_json.connect(
    ReadmarkAPI.on_thread_to_json, sender=thread_models.Thread)


class VotingAPI(voting.VotingAPI, comments_api.CommentsBase):
    voting_model = other_models.VotingVote


comment_signals.to_json.connect(
    VotingAPI.on_comment_to_json, sender=comment_models.Comment)
thread_signals.to_json.connect(
    VotingAPI.on_thread_to_json, sender=thread_models.Thread)


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
            comments = comments.filter(role_id__in=[u.pk for u in users])
        if filter_not_users:
            users = story_models.Role.objects.filter(
                pk__in=filter_not_users, variation=self.variation)
            conditions.append(
                'Не от: ' + ', '.join([u.name for u in users]))
            comments = comments.exclude(role_id__in=[u.pk for u in users])
        return comments


class Likes(likes.Likes, comments_api.CommentsBase):
    like_model = other_models.CommentLike

    def create_like(self):
        like = super(Likes, self).create_like()
        # pylint: disable=E1137
        like.data['variation'] = {
            'id': self.variation.pk, 'name': self.variation.name}
        return like


class Favorites(likes.Favorites):
    like_model = other_models.CommentLike

    @staticmethod
    def like_data_to_json(likes_data):
        variations = {}
        for data in likes_data:
            variation_id = data['variation']['id']
            variations.setdefault(variation_id, {
                'name': data['variation']['name'],
                'items': []})
            variations[variation_id]['items'].append(data)
        return {
            'groups': [{
                'name': data['name'],
                'variation_id': variation_id,
                'items': data['items'],
            } for variation_id, data in variations.items()]
        }
