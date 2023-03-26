import os
import threading

import pytest

from tulius.core.elastic import indexing
from tulius.core.elastic import transport


@pytest.fixture(name='indexer_config')
def _test_indexer_config(tmp_path):
    return {
        'BASE_DIR': tmp_path,
        'transport': transport.TestTransport
    }


def test_creating_dirs(tmp_path):
    config = {
        'BASE_DIR': os.path.join(tmp_path, 'queue')
    }
    assert not os.path.exists(config['BASE_DIR'])
    with indexing.ElasticIndexer(config, autostart=False):
        pass
    # check created
    assert os.path.exists(config['BASE_DIR'])
    with indexing.ElasticIndexer(config):
        # check not fails when dirs already exist
        pass


def test_index_to_closed_indexer(indexer_config):
    indexer_config['PACK_SIZE'] = 1
    with indexing.ElasticIndexer(indexer_config, autostart=False) as indexer:
        pass
    with pytest.raises(indexing.ClosedException):
        indexer.index({})


def test_indexing_queue_if_transport_is_slow(indexer_config):
    indexer_config['PACK_SIZE'] = 1
    indexer_config['FILE_SIZE_LIMIT'] = 1
    with indexing.ElasticIndexer(indexer_config, autostart=False) as indexer:
        # send 3 documents, it must create queue of 3 files
        for i in range(3):
            if i == 2:
                # keep last record in current file
                indexer.file_size_limit = 10 * 1024
            indexer.index({'param': i})
        queue_files = list(os.scandir(indexer_config['BASE_DIR']))
        # two files per one queue element + dead queue
        assert len(queue_files) == 7
        waiter = threading.Event()
        queue = []

        def _signal(data, **kwargs):
            queue.append(data)
            if len(queue) >= 3:
                waiter.set()
        indexer.file_send_signal.connect(_signal)
        indexer.start_indexing()
        waiter.wait(60)
    assert len(queue) == 3
    # First must be sent first item
    assert queue[0][0].data['param'] == 0
    # then sent current file
    assert queue[1][0].data['param'] == 2
    # and items in queue
    assert queue[2][0].data['param'] == 1


def test_closing_module():
    indexer = indexing.get_indexer()
    assert indexer == indexing.get_indexer()  # gives same indexer
    indexing.close()
    indexing.close()  # can do twice nothing happen
    assert indexer != indexing.get_indexer()  # gives new after close


def test_closing_indexer_twice(indexer_config):
    with indexing.ElasticIndexer(indexer_config, autostart=False) as indexer:
        pass
    indexer.close()
    indexer.close()
