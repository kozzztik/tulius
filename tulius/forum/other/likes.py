import json

from django import http
from django import shortcuts
from django.core import exceptions

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

    def post(self, request, *args, **kwargs):
        data = json.loads(self.request.body)
        comment_id = data['id']
        value = data['value'] in ['true', True]
        try:
            comment_id = int(comment_id)
        except:
            raise http.Http404()
        comment = shortcuts.get_object_or_404(models.Comment, id=comment_id)

        if not comment.parent.read_right(request.user):
            raise exceptions.PermissionDenied()

        like_marks = models.CommentLike.objects.filter(
            user=request.user, comment=comment)
        if value:
            if not like_marks:
                like_mark = models.CommentLike(
                    user=request.user, comment=comment)
                like_mark.save()
        else:
            for like in like_marks:
                like.delete()
        return {'value': value}
