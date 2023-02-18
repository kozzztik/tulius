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
from django.core.serializers.json import DjangoJSONEncoder
import elasticsearch8

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
    record = bytes(json.dumps(data, cls=DjangoJSONEncoder), 'utf-8') + b'\n'
    for h in logger.handlers:
        if isinstance(h, (handlers.SocketHandler, handlers.DatagramHandler)):
            h.send(record)


def do_direct_index(instance, **_kwargs):
    """ For testing, to be sure that data visible to search immediately """
    # pylint: disable=unexpected-keyword-arg
    client.index(
        id=instance.pk, index=index_name(instance.__class__),
        document=instance_to_document(instance), refresh='wait_for')


client = elasticsearch8.Elasticsearch(hosts=settings.ELASTIC_HOSTS)


def queryset_iterator(queryset, chunk_size=1000):
    """
    Iterate over a Django Queryset ordered by the primary key

    This method loads a maximum of chunk_size (default: 1000) rows in it's
    memory at the same time while django normally would load all rows in it's
    memory. Using the iterator() method only causes it to not preload all the
    classes.

    Note that the implementation of the iterator does not support ordered
    query sets.
    """
    pk = 0
    last_pk = queryset.order_by('-pk')[0].pk
    queryset = queryset.order_by('pk')
    while pk < last_pk:
        for row in queryset.filter(pk__gt=pk)[:chunk_size]:
            pk = row.pk
            yield row
        gc.collect()


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
        response = client.bulk(body=data)
        if response['errors']:
            raise ValueError('errors occurred during request')

    def __call__(self, query):
        counter = 0
        bulk = []
        all_count = query.count()
        self.progress(counter, all_count)
        if not all_count:
            return
        for instance in queryset_iterator(query, chunk_size=self.chunk_size):
            bulk.append(instance_to_document(instance))
            if len(bulk) >= self.bulk_size:
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
