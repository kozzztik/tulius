import json

from django import http
from django import shortcuts
from django.core import exceptions
from django.db import transaction

from tulius.forum import plugins
from tulius.forum import models
from tulius.forum.comments import api


class Likes(plugins.BaseAPIView):
    require_user = False

    def get(self, request, *args, **kwargs):
        data = request.GET['ids'].split(',')
        ids = [int(pk) for pk in data]
        response = {pk: False for pk in ids}
        like_marks = models.CommentLike.objects.filter(
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
            models.Comment.objects.select_for_update(), id=comment_id)

        like_marks = models.CommentLike.objects.filter(
            user=request.user, comment=comment)
        if value:
            if not like_marks:
                like_mark = models.CommentLike(
                    user=request.user, comment=comment)
                like_mark.save()
                comment.likes += 1
                comment.save()
        else:
            like_marks.delete()
            comment.likes -= 1
            comment.save()
        return {'value': value}


class Favorites(plugins.BaseAPIView):
    require_user = True
    comments_class = api.CommentAPI

    def get_view(self, comment):
        view = self.comments_class()
        view.setup(self.request)
        view.user = self.user
        view.comment = comment
        return view

    def get_comments(self):
        likes = models.CommentLike.objects.select_related('comment').filter(
            user=self.user, comment__plugin_id=self.comments_class.plugin_id)
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
    def comments_to_json(views):
        return {
            'groups': [{
                'name': 'Форум',
                'items': [{
                    'comment': view.comment_to_json(view.comment),
                    'thread': view.obj_to_json(),
                } for view in views],
            }],
        }

    def get_context_data(self, **kwargs):
        comments = self.get_comments()
        return self.comments_to_json(comments)
