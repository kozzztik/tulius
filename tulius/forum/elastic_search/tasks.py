from celery import shared_task
from django import apps
from django.conf import settings

from tulius.forum.elastic_search import models
from tulius.forum.elastic_search import mapping
from tulius.websockets import publisher
from tulius.websockets import consts


class ReindexAll(models.ReindexQuery):

    def __init__(self, model_name, user_id, counters):
        super().__init__()
        self.model_name = model_name
        self.user_id = user_id
        self.counters = counters

    def progress(self, counter, all_count):
        self.counters[self.model_name] = {
            'count': counter,
            'all_count': all_count
        }
        publisher.publish_message(
            consts.CHANNEL_USER.format(self.user_id), {
                '.direct': True,
                '.action': 'index_all_elastic_search',
                '.namespaced': 'task_update',
                'finished': False,
                'counters': self.counters
            })


@shared_task(track_started=True)
def reindex_all_entities(user_id):
    counters = {}
    for app_name, model_name in settings.ELASTIC_MODELS:
        model = apps.apps.get_model(app_name, model_name)
        mapping.rebuild_index(model)
        ReindexAll(f'{app_name}.{model_name}', user_id, counters)(
            model.objects.all())
    publisher.publish_message(
        consts.CHANNEL_USER.format(user_id), {
            '.direct': True,
            '.action': 'index_all_elastic_search',
            '.namespaced': 'task_update',
            'finished': True,
            'counters': counters
        })


class ReindexComments(models.ReindexQuery):
    def __init__(self, user_id, counters):
        super().__init__()
        self.user_id = user_id
        self.counters = counters
        self.reported = False

    def progress(self, counter, all_count):
        if not self.reported:
            self.reported = True
            self.counters['comments'] += all_count
            publisher.publish_message(
                consts.CHANNEL_USER.format(self.user_id), {
                    '.direct': True,
                    '.action': 'index_forum_elastic_search',
                    '.namespaced': 'task_update',
                    'finished': False,
                    'threads': self.counters['threads'],
                    'comments': self.counters['comments'],
                })


@shared_task(track_started=True)
def reindex_forum(app_label, model_name, parent_id, user_id):
    thread_model = apps.apps.get_model(app_label, model_name)
    threads_query = thread_model.objects.all()
    if parent_id:
        threads_query = threads_query.filter(parents_ids__contains=parent_id)
    counters = {
        'threads': 0,
        'comments': 0,
    }
    for thread in threads_query.iterator(chunk_size=100):
        models.client.index(
            models.index_name(thread_model),
            models.instance_to_document(thread),
            id=thread.pk)
        counters['threads'] += 1
        if not thread.room:
            ReindexComments(user_id, counters)(thread.comments)
    publisher.publish_message(
        consts.CHANNEL_USER.format(user_id), {
            '.direct': True,
            '.action': 'index_forum_elastic_search',
            '.namespaced': 'task_update',
            'finished': True,
            'threads': counters['threads'],
            'comments': counters['comments'],
        })


@shared_task(track_started=True)
def after_update_rights(app_label, model_name, thread_id):
    thread_model = apps.apps.get_model(app_label, model_name)
    instance = thread_model.objects.get(pk=thread_id)
    if instance.room:
        threads = thread_model.objects.filter(
            parents_ids__contains=thread_id, room=False)
    else:
        threads = [instance]
    for thread in threads:
        models.ReindexQuery()(thread.comments)
