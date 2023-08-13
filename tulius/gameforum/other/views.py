from tulius.forum.comments import signals as comment_signals
from tulius.forum.threads import signals as thread_signals
from tulius.forum.other import voting
from tulius.forum.other import likes
from tulius.gameforum.threads import models as thread_models
from tulius.gameforum.threads import views as thread_views
from tulius.gameforum.comments import views as comments_api
from tulius.gameforum.comments import models as comment_models
from tulius.gameforum.other import models as other_models
from tulius.stories import models as story_models
from tulius.forum.elastic_search import views as elastic_search


class VotingAPI(voting.VotingAPI, comments_api.CommentsBase):
    voting_model = other_models.VotingVote


comment_signals.to_json.connect(
    VotingAPI.on_comment_to_json, sender=comment_models.Comment)
thread_signals.to_json.connect(
    VotingAPI.on_thread_to_json, sender=thread_models.Thread)


class Search(elastic_search.Search, thread_views.BaseThreadAPI):
    comment_model = comment_models.Comment

    def apply_users_filters(self, search_request, conditions, data):
        filter_users = data.get('users', [])
        filter_users = [int(u) for u in filter_users]
        filter_not_users = data.get('not_users', [])
        filter_not_users = [int(u) for u in filter_not_users]
        if filter_users:
            users = story_models.Role.objects.filter(
                pk__in=filter_users, variation=self.variation)
            pks = [u.pk for u in users]
            names = [u.name for u in users]
            if 0 in filter_users:
                pks.append(0)
                names.append('---')
            conditions.append('От: ' + ', '.join(names))
            search_request['must'].append(
                {'terms': {'role_id': pks}},
            )
        if filter_not_users:
            users = story_models.Role.objects.filter(
                pk__in=filter_not_users, variation=self.variation)
            pks = [u.pk for u in users]
            names = [u.name for u in users]
            if 0 in filter_not_users:
                pks.append(0)
                names.append('---')
            conditions.append(
                'Не от: ' + ', '.join(names))
            search_request['must_not'].append(
                {'terms': {'role_id': pks}},
            )

    def comments_query(self, pks):
        comments = list(self.comment_model.objects.filter(
            pk__in=pks, parent__variation=self.variation, deleted=False,
            parent__deleted=False,
        ).select_related('parent'))
        for comment in comments:
            # to reuse roles cache
            comment.parent.variation = self.variation
        return comments

    def options(self, request, *args, **kwargs):
        add_leader = False
        if 'pks' in request.GET:
            pks = request.GET['pks'].split(',')
            users = story_models.Role.objects.filter(
                deleted=False, pk__in=pks, variation=self.variation)
            if '0' in pks:
                add_leader = True
        else:
            users = story_models.Role.objects.filter(
                deleted=False, name__istartswith=request.GET['query'],
                variation=self.variation
            )[:10]
        users = [{"id": u.pk, "title": u.name} for u in users]
        if add_leader:
            users.append({'id': 0, 'title': '---'})
        return {"users": users}


class Likes(likes.Likes, comments_api.CommentsBase):
    like_model = other_models.CommentLike

    def create_like(self):
        like = super().create_like()
        game = self.variation.game
        # pylint: disable=unsupported-assignment-operation
        like.data['variation'] = {
            'id': self.variation.pk,
            'name': str(game) if game else self.variation.name}
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


class ReindexForum(elastic_search.ReindexForum):
    thread_model = thread_models.Thread
