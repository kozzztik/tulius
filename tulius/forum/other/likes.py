import json

from django import http
from django import shortcuts
from django.db import transaction

from tulius.forum import plugins
from tulius.forum import models


class Likes(plugins.BaseAPIView):
    require_true = False

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
