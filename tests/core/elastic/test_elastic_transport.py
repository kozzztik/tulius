import time

import threading
import os
from unittest import mock

import pytest
import elasticsearch8
from django.conf import settings

from tulius.core.elastic import indexing
from tulius.core.elastic import files
from tulius.core.elastic import transport


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
        'PACK_SIZE': 3,
    }
    event = threading.Event()

    with indexing.ElasticIndexer(config) as indexer:
        indexer.file_send_signal.connect(lambda **kwargs: event.set())
        indexer.index({
            '_index': es_index,
            '_id': 1,
            'param': 1,
            'param2': 1,
        })
        # this document should be fine
        indexer.index({
            '_index': es_index,
            '_id': 2,
            'param': 'str',
            'param2': 2,
        })
        # this document must be rejected by ES
        indexer.index({
            '_index': es_index,
            '_id': 3,
            'param': 'str',
            'param2': 'str',
        })
        event.wait(60)
    es_client.indices.refresh(index=es_index)
    response = es_client.search(index=es_index)
    hits = response['hits']['hits']
    # checks that template works - even first event was int, both
    # event considered strings
    assert len(hits) == 2  # both indexed, no miss
    # read dead queue
    files_list = list(os.scandir(indexer.dead_queue_dir))
    assert len(files_list) == 2
    rec = files_list.pop()
    name = os.path.splitext(rec.name)[0]
    queue = files.DeadQueueFile(indexer.config, name)
    bulk = queue.read_bulk(10)
    assert len(bulk) == 1
    assert bulk[0].data['_id'] == 3
    assert 'failed to parse' in bulk[0].exc


def test_completely_invalid_templates(tmp_path, es_index):
    config = {
        'BASE_DIR': tmp_path,
        'INDEX_TEMPLATES': object(),
        'PACK_SIZE': 1,
    }
    event = threading.Event()
    with indexing.ElasticIndexer(config) as indexer:
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


def test_doc_no_index(tmp_path):
    config = {
        'BASE_DIR': tmp_path,
        'PACK_SIZE': 1,
    }
    event = threading.Event()
    with indexing.ElasticIndexer(config) as indexer:
        indexer.file_send_signal.connect(lambda **kwargs: event.set())
        indexer.index({
            '_id': 1,
            'param': 1,
        })
        event.wait(60)
        files_list = list(os.scandir(indexer.dead_queue_dir))
        assert len(files_list) == 2
        files_list = [f.path for f in files_list if f.name.endswith('.log')]
        rec = files_list.pop()
        assert os.path.getsize(rec) > 0


def test_connection_refused(tmp_path, es_index):
    config = {
        'BASE_DIR': tmp_path,
        'PACK_SIZE': 1,
    }
    event = threading.Event()
    with indexing.ElasticIndexer(config) as indexer:
        with mock.patch.object(indexing, 'time') as time_mock:
            time_mock.time = time.time
            with mock.patch.object(indexer.transport, 'client') as es_mock:
                es_mock.bulk.side_effect = [
                    elasticsearch8.ConnectionError('error'),
                    {'errors': []}
                ]
                indexer.file_send_signal.connect(lambda **kwargs: event.set())
                indexer.index({
                    '_index': es_index,
                    '_id': 1,
                    'param': 1,
                })
                event.wait(60)
    assert time_mock.sleep.called
    assert time_mock.sleep.call_count == 1
    assert time_mock.sleep.call_args[0][0] == indexer.send_period
    assert es_mock.bulk.call_count == 2


def test_basic_transport():
    obj = transport.BaseTransport({})
    obj.init_indexing()  # not fails
    with pytest.raises(NotImplementedError):
        obj.do_index({})  # fails
