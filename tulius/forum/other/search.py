import json
import datetime

from django import http
from django.contrib import auth
from django.core import exceptions
from django.utils import timezone

from tulius.forum import core
from tulius.forum.comments import views


def get_datetime(text):
    try:
        date = datetime.datetime.strptime(text, "%d.%m.%Y")
    except:
        return None
    return datetime.datetime(
        date.year, date.month, date.day,
        tzinfo=timezone.get_current_timezone())


class Search(core.BaseAPIView):
    require_user = True
    comments_class = views.CommentAPI

    def get_view(self, comment):
        view = self.comments_class()
        view.setup(self.request)
        view.user = self.user
        view.comment = comment
        return view

    @staticmethod
    def apply_users_filters(comments, conditions, data):
        filter_users = data.get('users', [])
        filter_not_users = data.get('not_users', [])
        if filter_users:
            users = auth.get_user_model().objects.filter(pk__in=filter_users)
            conditions.append('От: ' + ', '.join([u.username for u in users]))
            comments = comments.filter(user__in=users)
        if filter_not_users:
            users = auth.get_user_model().objects.filter(
                pk__in=filter_not_users)
            conditions.append(
                'Не от: ' + ', '.join([u.username for u in users]))
            comments = comments.exclude(user__in=users)
        return comments

    def post(self, request, pk, **_kwargs):
        data = json.loads(request.body)
        thread_view = self.get_view(None)
        thread_view.get_parent_thread(pk)
        comments = self.comments_class.comment_model.objects.select_related(
            'parent').filter(
                parent__tree_id=thread_view.obj.tree_id,
                parent__lft__gte=thread_view.obj.lft,
                parent__rght__lte=thread_view.obj.rght)
        filter_date_from = data.get('date_from', [])
        filter_date_to = data.get('date_to', [])
        filter_text = data.get('text', [])
        conditions = []
        comments = self.apply_users_filters(comments, conditions, data)

        if filter_date_from:
            date = get_datetime(filter_date_from)
            conditions.append(f'От даты: {filter_date_from}')
            if date:
                comments = comments.filter(create_time__gte=date)

        if filter_date_to:
            date = get_datetime(filter_date_to)
            conditions.append(f'До даты: {filter_date_to}')
            if date:
                comments = comments.filter(create_time__lte=date)

        if filter_text:
            conditions.append(f'С текстом: {filter_text}')
            comments = comments.filter(body__icontains=filter_text)
        search_results = []
        for comment in comments:
            view = self.get_view(comment)
            try:
                view.get_parent_thread(comment.parent_id)
            except exceptions.PermissionDenied:
                continue
            except http.Http404:
                continue
            search_results.append(view)
            if len(search_results) >= 50:
                break
        return {
            'thread': thread_view.obj_to_json(),
            'conditions': conditions,
            'results': [{
                'comment': view.comment_to_json(view.comment),
                'thread': view.obj_to_json(),
            } for view in search_results]
        }

    def options(self, request, *args, **kwargs):
        users = auth.get_user_model().objects.filter(
            is_active=True, username__istartswith=request.GET['query'])[:10]
        return {
            "users": [{"id": u.pk, "title": u.username} for u in users]
        }
