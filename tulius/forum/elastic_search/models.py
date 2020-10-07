import gc
import json
import logging
import datetime
from logging import handlers

from django.apps import apps
from django.conf import settings
from django.db import models
from django.db.models import signals
from django.db.models.fields import related
from django.db.models.fields import reverse_related
import elasticsearch7

logger = logging.getLogger('elastic_search_indexing')


def index_name(model):
    s = f"{model._meta.app_label}_{model._meta.object_name}"
    return f"{settings.ELASTIC_PREFIX}_{s}".lower()


ignore_field_types = (
    related.RelatedField,
    reverse_related.ForeignObjectRel,
    models.AutoField,
    models.FileField,
)


def instance_to_document(instance):
    data = {}
    for field in instance.__class__._meta.get_fields(include_hidden=True):
        if not isinstance(field, ignore_field_types):
            value = getattr(instance, field.name)
            if isinstance(value, datetime.date):
                value = value.isoformat()
            data[field.column] = value
    if hasattr(instance, 'to_elastic_search'):
        instance.to_elastic_search(data)
    data['pk'] = instance.pk
    data['message'] = index_name(instance.__class__)
    return data


def do_index(instance, **_kwargs):
    data = instance_to_document(instance)
    record = bytes(json.dumps(data), 'utf-8')
    for h in logger.handlers:
        if isinstance(h, (handlers.SocketHandler, handlers.DatagramHandler)):
            h.send(record)


client = elasticsearch7.Elasticsearch(hosts=settings.ELASTIC_HOSTS)


class ReindexQuery:
    chunk_size = 1000
    counter_chunk = 1000
    bulk_size = 50

    def progress(self, counter, all_count):
        pass

    @staticmethod
    def bulk_index(bulk):
        data = []
        for instance in bulk:
            data.append({
                'index': {
                    '_index': instance['message'],
                    '_id': instance['pk']
                }
            })
            data.append(instance)
        response = client.bulk(data)
        if response['errors']:
            raise Exception('errors occured during request')

    def __call__(self, query):
        counter = 0
        bulk = []
        all_count = query.count()
        self.progress(counter, all_count)
        for instance in query.iterator(chunk_size=self.chunk_size):
            bulk.append(instance_to_document(instance))
            if len(bulk) >= 50:
                self.bulk_index(bulk)
                bulk = []
            counter += 1
            if counter % self.counter_chunk == 0:
                gc.collect()
                self.progress(counter, all_count)
        if bulk:
            self.bulk_index(bulk)
        self.progress(counter, all_count)


def init():
    for app_name, model_name in settings.ELASTIC_MODELS:
        model = apps.get_model(app_name, model_name)
        signals.post_save.connect(do_index, sender=model, weak=False)