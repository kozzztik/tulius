from tulius.forum.other import readmarks
from tulius.forum.other import likes
from tulius.forum.other import search
from tulius.forum.voting import views as voting
from tulius.gameforum import base
from tulius.gameforum.threads import api as threads
from tulius.gameforum.comments import api as comments_api
from tulius.stories import models as story_models


class ReadmarkAPI(readmarks.ReadmarkAPI, threads.BaseThreadAPI):
    pass


class VotingAPI(voting.VotingAPI, comments_api.CommentsBase):
    pass


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
    def comments_to_json(views):
        variations = {}
        for api in views:
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
