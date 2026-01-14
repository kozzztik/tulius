import logging
import os

from unittest import mock

from tulius.core.elastic import indexing
from tulius.core.elastic import handler


def test_log_objects(tmp_path):
    config = {
        'BASE_DIR': os.path.join(tmp_path, 'queue'),
        'HOSTS': 'http://127.0.0.1:9200'
    }
    logger = logging.Logger(__name__)
    logger.propagate = False
    logger.handlers = [handler.Handler(autostart=False, **config)]
    index = mock.MagicMock()
    with mock.patch.object(indexing.ElasticIndexer, 'index', index):
        logger.error('Test', extra={'obj': object()})
    assert index.called
    record = index.call_args[0][0]
    assert record['message'] == 'Test'
    assert '<object object at ' in record['obj']


def test_log_exception(tmp_path):
    config = {
        'BASE_DIR': os.path.join(tmp_path, 'queue'),
        'HOSTS': 'http://127.0.0.1:9200'
    }
    logger = logging.Logger(__name__)
    logger.propagate = False
    logger.handlers = [handler.Handler(autostart=False, **config)]
    index = mock.MagicMock()
    with mock.patch.object(indexing.ElasticIndexer, 'index', index):
        try:
            raise ValueError('Test')
        except ValueError as exc:
            logger.exception(exc)
    assert index.called
    record = index.call_args[0][0]
    assert record['message'] == 'Test'
    assert 'stack_trace' in record
