import json

from django import http
from django import shortcuts
from django.core import exceptions
from django.db import transaction

from tulius.forum import core
from tulius.forum.other import models
from tulius.forum.comments import models as comment_models
from tulius.forum.comments import views


class Likes(core.BaseAPIView):
    like_model = models.CommentLike
    comment_model = comment_models.Comment
    require_user = False

    def get(self, request, *args, **kwargs):
        data = request.GET['ids'].split(',')
        ids = [int(pk) for pk in data]
        response = {pk: False for pk in ids}
        like_marks = self.like_model.objects.filter(
            user=request.user, comment_id__in=ids)
        for mark in like_marks:
            response[mark.comment_id] = True
        return response

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        comment_id = data['id']
        value = data['value'] in ['true', True]
        try:
            comment_id = int(comment_id)
        except:
            raise http.Http404()
        comment = shortcuts.get_object_or_404(
            self.comment_model.objects.select_for_update(), id=comment_id)

        like_marks = self.like_model.objects.filter(
            user=request.user, comment=comment)
        if value:
            if not like_marks:
                like_mark = self.like_model(
                    user=request.user, comment=comment)
                like_mark.save()
                comment.likes += 1
                comment.save()
        else:
            like_marks.delete()
            comment.likes -= 1
            comment.save()
        return {'value': value}


class Favorites(core.BaseAPIView):
    like_model = models.CommentLike
    require_user = True
    comments_class = views.CommentAPI

    def get_view(self, comment):
        view = self.comments_class()
        view.setup(self.request)
        view.user = self.user
        view.comment = comment
        return view

    def comments_query(self):
        return self.like_model.objects.select_related('comment').filter(
            user=self.user)

    def get_comments(self):
        likes = self.comments_query()
        comments = [like.comment for like in likes]
        result = []
        for comment in comments:
            view = self.get_view(comment)
            try:
                view.get_parent_thread(pk=comment.parent_id)
            except exceptions.PermissionDenied:
                continue
            result.append(view)
        return result

    @staticmethod
    def comments_to_json(view_objects):
        return {
            'groups': [{
                'name': 'Форум',
                'items': [{
                    'comment': view.comment_to_json(view.comment),
                    'thread': view.obj_to_json(),
                } for view in view_objects],
            }],
        }

    def get_context_data(self, **kwargs):
        comments = self.get_comments()
        return self.comments_to_json(comments)
