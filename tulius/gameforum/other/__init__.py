from tulius.forum.other import readmarks
from tulius.forum.other import likes
from tulius.forum.voting import views as voting
from tulius.gameforum.threads import api as threads
from tulius.gameforum.comments import api as comments
from tulius.stories import models as story_models


class ReadmarkAPI(readmarks.ReadmarkAPI, threads.BaseThreadAPI):
    pass


class VotingAPI(voting.VotingAPI, comments.CommentsBase):
    pass


class Favorites(likes.Favorites):
    comments_class = comments.CommentAPI
    variations = None

    def get_api(self, comment):
        api = super(Favorites, self).get_api(comment)
        tree_id = api.comment.parent.tree_id
        self.variations = self.variations or {}
        if tree_id not in self.variations:
            variation = story_models.Variation.objects.get(
                thread__tree_id=tree_id)
            self.variations[tree_id] = variation
        api.variation = self.variations[tree_id]
        return api

    @staticmethod
    def comments_to_json(comments):
        variations = {}
        for api in comments:
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
