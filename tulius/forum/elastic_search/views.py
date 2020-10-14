import math
import time
import datetime
import json

from django import dispatch
from django.core import exceptions
from django.contrib import auth
from django.conf import settings
from django.utils import timezone

from tulius.forum import core
from tulius.forum.threads import models as thread_models
from tulius.forum.elastic_search import tasks
from tulius.forum.rights import signals
from tulius.forum.comments import views
from tulius.forum.comments import pagination
from tulius.forum.elastic_search import models


class ReindexAll(core.BaseAPIView):
    def post(self, *_args, **_kwargs):
        if not self.user.is_superuser:
            raise exceptions.PermissionDenied()
        result = tasks.reindex_all_entities.apply_async(args=[self.user.pk])
        return {'task_id': result.id}


class ReindexForum(core.BaseAPIView):
    thread_model = thread_models.Thread

    def post(self, *_args, pk=None, **_kwargs):
        if not self.user.is_superuser:
            raise exceptions.PermissionDenied()
        result = tasks.reindex_forum.apply_async(
            args=[
                self.thread_model._meta.app_label,
                self.thread_model._meta.object_name,
                int(pk), self.user.pk])
        return {'task_id': result.id}


@dispatch.receiver(signals.after_update)
def after_update_rights(sender, instance, **_kwargs):
    tasks.after_update_rights.apply_async(args=[
        sender._meta.app_label, sender._meta.object_name, instance.pk])


def get_datetime(text):
    try:
        date = datetime.datetime.strptime(text, "%Y-%m-%d")
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
    def apply_users_filters(search_request, conditions, data):
        filter_users = data.get('users', [])
        filter_not_users = data.get('not_users', [])
        if filter_users:
            users = auth.get_user_model().objects.filter(pk__in=filter_users)
            conditions.append('От: ' + ', '.join([u.username for u in users]))
            search_request['must'].append(
                {'terms': {'user.id': [u.pk for u in users]}},
            )
        if filter_not_users:
            users = auth.get_user_model().objects.filter(
                pk__in=filter_not_users)
            conditions.append(
                'Не от: ' + ', '.join([u.username for u in users]))
            search_request['must_not'].append(
                {'terms': {'user.id': [u.pk for u in users]}},
            )

    @staticmethod
    def apply_dates_filters(search_request, conditions, data):
        filter_date_from = data.get('date_from', [])
        filter_date_to = data.get('date_to', [])
        if filter_date_from:
            date = get_datetime(filter_date_from)
            conditions.append(f'От даты: {filter_date_from}')
            if date:
                search_request['must'].append({'range': {'create_time': {
                    'gte': date.isoformat()
                }}})

        if filter_date_to:
            date = get_datetime(filter_date_to)
            conditions.append(f'До даты: {filter_date_to}')
            if date:
                search_request['must'].append({'range': {'create_time': {
                    'lte': date.isoformat()
                }}})

    def filter_rights(self, search_request):
        if not self.user.is_superuser:
            search_request['filter'] = {
                'bool': {
                    'should': [
                        {'term': {'public': True}},
                    ],
                    'minimum_should_match': 1,
                }
            }
            if self.user.is_authenticated:
                search_request['filter']['bool']['should'].append(
                    {'term': {'read_access': self.user.pk}},
                )

    def do_search(self, request, body):
        start_time = time.perf_counter_ns()
        response = models.client.search(
            index=models.index_name(self.comments_class.comment_model),
            body=body
        )
        hits = response['hits']['total']['value']
        request.profiling_data['elastic_time'] = response['took']
        request.profiling_data['elastic_full'] = \
            (time.perf_counter_ns() - start_time) / 1000000
        request.profiling_data['elastic_hits'] = hits
        return response

    def comments_query(self, pks):
        return self.comments_class.comment_model.objects.filter(
            pk__in=pks, deleted=False, parent__deleted=False
        ).select_related('user', 'parent')

    def post(self, request, **_kwargs):
        data = json.loads(request.body)
        page = int(data.get('page', 1))
        pk = data.get('thread_id', None)
        thread_view = None
        conditions = []
        if pk:
            pk = int(pk)
            thread_view = self.get_view(None)
            thread_view.get_parent_thread(pk)
            conditions.append(f'В: {thread_view.obj.title}')
        search_request = {
            'must': [],
            'filter': {},
            'must_not': [{'term': {'deleted': True}}]
        }
        self.filter_rights(search_request)
        if pk:
            search_request['must'].append(
                {'term': {'parents_ids': pk}})
        filter_text = data.get('text', [])
        self.apply_users_filters(search_request, conditions, data)
        self.apply_dates_filters(search_request, conditions, data)

        if filter_text:
            conditions.append(f'С текстом: {filter_text}')
            search_request['must'].append({
                'match': {
                    'body': {
                        'query': filter_text,
                        'fuzziness': 'AUTO',
                    }
                }
            })
        for name in ['must', 'filter', 'must_not']:
            if not search_request[name]:
                del search_request[name]
        comments_on_page = self.comments_class.comment_model.COMMENTS_ON_PAGE
        body = {
            'query': {'bool': search_request},
            '_source': False,
            'from': (page - 1) * comments_on_page,
            'size': comments_on_page,
            'explain': settings.DEBUG,
        }
        if filter_text:
            body['highlight'] = {
                'pre_tags': ['[search]'],
                'post_tags': ['[/search]'],
                'number_of_fragments': 0,
                'fields': {
                    'body': {}
                }
            }

        response = self.do_search(request, body)

        hits = response['hits']['total']['value']
        page_count = math.ceil(hits / comments_on_page)
        request.profiling_data['elastic_page'] = page
        request.profiling_data['elastic_page_count'] = page_count
        pks = [int(hit['_id']) for hit in response['hits']['hits']]
        comments = list(self.comments_query(pks))
        comments.sort(key=lambda x: pks.index(x.pk))
        search_results = []
        hits = {int(hit['_id']): hit for hit in response['hits']['hits']}
        for comment in comments:
            if filter_text:
                # found text hightlighting
                comment.body = hits[comment.pk]['highlight']['body'][0]
            if not comment.parent.read_right(self.user):
                continue
            search_results.append(comment)
        return {
            'took': response['took'],
            'page': page,
            'page_count': page_count,
            'pagination': pagination.get_pagination_context(
                self.request, page, max(page_count, 1)),
            'thread': thread_view.obj_to_json() if thread_view else None,
            'conditions': conditions,
            'results': [{
                'comment': comment.to_json(self.user, detailed=True),
                'thread': {
                    'id': comment.parent.pk,
                    'rights': comment.parent.rights_to_json(self.user)
                },
            } for comment in search_results]
        }

    def options(self, request, *args, **kwargs):
        if 'pks' in request.GET:
            pks = request.GET['pks'].split(',')
            users = auth.get_user_model().objects.filter(
                is_active=True, pk__in=pks)
        else:
            users = auth.get_user_model().objects.filter(
                is_active=True, username__istartswith=request.GET['query']
            )[:10]
        return {
            'users': [{'id': u.pk, 'title': u.username} for u in users]
        }
