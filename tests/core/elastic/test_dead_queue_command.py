from unittest import mock

from django.core.management import execute_from_command_line

from tulius.core.elastic import transport
from tulius.core.elastic import indexing


def test_push_command(tmp_path):
    indexer_config = {
        'BASE_DIR': tmp_path,
        'transport': transport.TestTransport
    }
    indexing.close()
    with indexing.ElasticIndexer(indexer_config) as indexer:
        indexer._write_to_dead_queue(ValueError(), b'42')
    with indexing.ElasticIndexer(indexer_config) as indexer:
        with mock.patch.object(indexing, '_indexer', indexer):
            execute_from_command_line(['manage.py', 'push_dead_queue'])
    assert len(indexer.transport.queue) == 1
    assert indexer.transport.queue[0][0].data == 42
