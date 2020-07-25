import json

from django.db import transaction

from tulius.forum import core
from tulius.forum.other import models
from tulius.forum.comments import views


class Likes(views.CommentBase):
    like_model = models.CommentLike
    require_user = True

    def get(self, request, *args, **kwargs):
        data = request.GET['ids'].split(',')
        ids = [int(pk) for pk in data]
        response = {pk: False for pk in ids}
        like_marks = self.like_model.objects.filter(
            user=request.user, comment_id__in=ids)
        for mark in like_marks:
            response[mark.comment_id] = True
        return response

    def create_like(self):
        like_mark = self.like_model(user=self.user, comment=self.comment)
        # pylint: disable=E1137
        like_mark.data['comment'] = self.comment_to_json(self.comment)
        like_mark.data['thread'] = self.obj_to_json()  # pylint: disable=E1137
        return like_mark

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        comment_id = int(data['id'])
        value = data['value'] in ['true', True]
        like_marks = self.like_model.objects.filter(
            user=request.user, comment_id=comment_id)
        if value:
            if not like_marks:
                self.get_comment(comment_id, for_update=True)
                like_mark = self.create_like()
                like_mark.save()
                self.comment.likes += 1
                self.comment.save()
        else:
            comment = self.comment_model.objects.select_for_update().get(
                pk=comment_id)
            like_marks.delete()
            comment.likes -= 1
            comment.save()
        return {'value': value}


class Favorites(core.BaseAPIView):
    like_model = models.CommentLike
    require_user = True

    def get_likes(self):
        likes = self.like_model.objects.select_related('comment').filter(
            user=self.user)
        return [like.data for like in likes]

    @staticmethod
    def like_data_to_json(likes_data):
        return {
            'groups': [{
                'name': 'Форум',
                'items': likes_data,
            }],
        }

    def get_context_data(self, **kwargs):
        likes_data = self.get_likes()
        return self.like_data_to_json(likes_data)
