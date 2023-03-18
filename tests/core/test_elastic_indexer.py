import os
import threading

import pytest
from django.conf import settings
import elasticsearch8

from tulius.core import elastic_indexer


def test_creating_dirs(tmp_path):
    config = {
        'BASE_DIR': os.path.join(tmp_path, 'queue')
    }
    assert not os.path.exists(config['BASE_DIR'])
    with elastic_indexer.ElasticIndexer(config):
        pass
    # check created
    assert os.path.exists(config['BASE_DIR'])
    with elastic_indexer.ElasticIndexer(config):
        # check not fails when dirs already exist
        pass


es_client = elasticsearch8.Elasticsearch(hosts=settings.ELASTIC_HOSTS)


@pytest.fixture(name='es_session_index', scope='session')
def es_session_index_fixture():
    index_name = 'tmp_indexer_test_session_index'
    try:
        es_client.indices.delete(index=index_name)
    except elasticsearch8.NotFoundError:
        pass
    es_client.indices.create(index=index_name)
    yield index_name
    es_client.indices.delete(index=index_name)


@pytest.fixture(name='es_index')
def es_index_fixture():
    index_name = 'tmp_indexer_test_index'
    try:
        es_client.indices.delete(index=index_name)
    except elasticsearch8.NotFoundError:
        pass
    yield index_name
    try:
        es_client.indices.delete(index=index_name)
    except elasticsearch8.NotFoundError:
        pass


@pytest.fixture(name='es_index_template')
def es_index_template_fixture():
    template_name = 'tmp_indexer_test_template'
    try:
        es_client.indices.delete_template(name=template_name)
    except elasticsearch8.NotFoundError:
        pass
    yield template_name
    try:
        es_client.indices.delete_template(name=template_name)
    except elasticsearch8.NotFoundError:
        pass


def test_full_cycle(tmp_path, es_index, es_index_template):
    config = {
        'BASE_DIR': os.path.join(tmp_path, 'queue'),
        'INDEX_TEMPLATES': {
            # this checks that invalid templates doesn't brake indexing
            es_index_template + 'broken': {
                'index_patterns': [es_index + 'broken'],
                'template': {
                    'mappings': {
                        'param': {'type': 'foobar'}
                    }
                }
            },
            # this not brakes too
            'some_template': object(),
            es_index_template: {
                'index_patterns': [es_index],
                'template': {
                    'mappings': {
                        'properties': {
                            'param': {'type': 'text'}
                        }
                    }
                }
            }
        },
        'PACK_SIZE': 2,
    }
    event = threading.Event()

    with elastic_indexer.ElasticIndexer(config) as indexer:
        indexer.file_send_signal.connect(lambda **kwargs: event.set())
        indexer.index({
            '_index': es_index,
            '_id': 1,
            'param': 1,
        })
        indexer.index({
            '_index': es_index,
            '_id': 2,
            'param': 'str',
        })
        event.wait(60)
    es_client.indices.refresh(index=es_index)
    response = es_client.search(index=es_index)
    hits = response['hits']['hits']
    # checks that template works - even first event was int, both
    # event considered strings
    assert len(hits) == 2  # both indexed, no miss


def test_completely_invalid_templates(tmp_path, es_index):
    config = {
        'BASE_DIR': tmp_path,
        'INDEX_TEMPLATES': object(),
        'PACK_SIZE': 1,
    }
    event = threading.Event()
    with elastic_indexer.ElasticIndexer(config) as indexer:
        indexer.file_send_signal.connect(lambda **kwargs: event.set())
        indexer.index({
            '_index': es_index,
            '_id': 1,
            'param': 1,
        })
        event.wait(60)
    es_client.indices.refresh(index=es_index)
    response = es_client.search(index=es_index)
    hits = response['hits']['hits']
    # indexing not broken by invalid config
    assert len(hits) == 1
