import logging

import elasticsearch8
from django.conf import settings
from django.utils import module_loading
from django.core import exceptions


logger = logging.getLogger('deferred_indexing')


class TransportNotReady(Exception):
    pass


class BaseTransport:
    def __init__(self, config):
        self.config = config

    def init_indexing(self):
        pass

    def do_index(self, data):
        raise NotImplementedError


class TestTransport(BaseTransport):
    def __init__(self, config):
        super().__init__(config)
        self.queue = []

    def do_index(self, data):
        self.queue.append(data)


class ElasticTransport(BaseTransport):
    def __init__(self, config):
        super().__init__(config)
        self.timeout = self.config.get('TIMEOUT', 60)
        self.client = elasticsearch8.Elasticsearch(
            hosts=settings.ELASTIC_HOSTS, request_timeout=self.timeout)

    def init_indexing(self):
        try:
            templates = self.config.get('INDEX_TEMPLATES') or {}
            for name, template in templates.items():
                try:
                    if isinstance(template, str):
                        template = module_loading.import_string(template)
                    elif isinstance(template, dict):
                        template = template.copy()
                    else:
                        raise exceptions.ImproperlyConfigured(
                            'Elastic index template must be str or dict')
                    self.client.indices.put_index_template(
                        name=name, **template)
                except Exception as exc:
                    logger.error(
                        'Failed to install template %s: %s', name, exc)
        except Exception as exc:
            logger.exception('Failed to install index templates: %s', exc)

    def do_index(self, data):
        operations = []
        queue = []
        for entity in data:
            doc = entity.data.copy()
            if '_index' not in doc:
                entity.exc = "No _index in document"
                continue
            operations.append({
                doc.pop('_action', 'index'): {
                    '_index': doc.pop('_index'),
                    '_id': doc.pop('_id', None)
                }
            })
            queue.append(entity)
            operations.append(doc)
        if operations:
            try:
                response = self.client.bulk(
                    operations=operations, refresh=False)
            except elasticsearch8.ConnectionError as exc:
                raise TransportNotReady() from exc
            if response['errors']:
                for i, item in enumerate(response['items']):
                    item = list(item.values())[0]
                    if item['status'] in (200, 201):
                        continue
                    queue[i].exc = item.get('error')
