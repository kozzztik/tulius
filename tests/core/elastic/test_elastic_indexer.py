import json

import os
import threading
import multiprocessing
from unittest import mock

import pytest

from tulius.core.elastic import indexing
from tulius.core.elastic import files
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
        # check that file rotating keeps write caching in current file
        assert len(indexer._work_files) == 1
        assert indexer._work_files[0].write_caching
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


def test_transport_import(indexer_config):
    indexer_config['transport'] = 'tulius.core.elastic.transport.BaseTransport'
    with indexing.ElasticIndexer(indexer_config, autostart=False) as indexer:
        assert isinstance(indexer.transport, transport.BaseTransport)


def test_broken_file_format(indexer_config):
    with open(os.path.join(indexer_config['BASE_DIR'], 'my.log'), 'wb') as f:
        f.write(b'smth\n')
    event = threading.Event()
    with indexing.ElasticIndexer(indexer_config, autostart=False) as indexer:
        indexer.file_send_signal.connect(lambda **kwargs: event.set())
        indexer.start_indexing()
        event.wait(60)
    files_list = list(os.scandir(indexer.dead_queue_dir))
    assert len(files_list) == 2
    rec = files_list.pop()
    name = os.path.splitext(rec.name)[0]
    queue = files.DeadQueueFile(indexer.config, name)
    bulk = queue.read_bulk(10)
    assert len(bulk) == 1
    assert bulk[0].data == b'smth\n'


class Process(multiprocessing.Process):
    def __init__(self, config, name):
        self.ready = multiprocessing.Event()
        self.finish = multiprocessing.Event()
        self.config = config
        self.file_name = name
        super().__init__()

    def run(self):
        queue = files.DeadQueueFile(self.config, self.file_name)
        try:
            queue.write_data(('smth', {'param': 2}))
            self.ready.set()
            self.finish.wait(60)
        finally:
            queue.close()


class FailingTransport(transport.BaseTransport):
    def do_index(self, data):
        for item in data:
            item.exc = 'foobar'


def test_dead_queue(indexer_config):
    indexer_config['transport'] = FailingTransport
    indexer_config['PACK_SIZE'] = 1
    indexer_config['FILE_SIZE_LIMIT'] = 1
    event = threading.Event()
    with indexing.ElasticIndexer(indexer_config, autostart=False) as indexer:
        indexer.file_send_signal.connect(lambda **kwargs: event.set())
        indexer.start_indexing()
        indexer.index({'param': 0})
        event.wait(60)
        assert event.is_set()
        event.clear()
        indexer.index({'param': 1})
        event.wait(60)
        assert event.is_set()
    files_list = list(os.scandir(indexer.dead_queue_dir))
    assert len(files_list) == 4
    indexer_config['transport'] = transport.TestTransport
    # add some trash there, directory
    # important to add .log so be sure we not assume directory as work file
    os.makedirs(
        os.path.join(indexer.dead_queue_dir, 'foobar.log'), exist_ok=True)
    # add one file with wrong extension
    with open(os.path.join(indexer.dead_queue_dir, 'some.txt'), 'tw') as f:
        json.dump({'param': 1}, f)
    # add one busy file
    process = Process(indexer.config, 'barfoo')
    process.start()
    try:
        process.ready.wait(60)
        with indexing.ElasticIndexer(
                indexer_config, autostart=False) as indexer:
            with mock.patch.object(indexing.logger, 'error') as error_mock:
                indexer.push_dead_queue()
    finally:
        process.finish.set()
        process.join(50)
    # no errors like try to get folder as work file, only locking busy file
    assert error_mock.called
    assert error_mock.call_count == 1
    assert 'File is busy' in error_mock.call_args.args[0]
    assert 'barfoo' in error_mock.call_args.args[1]
    assert len(indexer.transport.queue) == 2


class DeferredProcess(Process):
    def run(self):
        queue = files.WorkFile(self.config, self.file_name)
        try:
            queue.write_data({'param': 7})
            self.ready.set()
            self.finish.wait(60)
        finally:
            queue.close()


def test_deferred_queue(indexer_config):
    indexer_config['PACK_SIZE'] = 1
    indexer_config['FILE_SIZE_LIMIT'] = 1
    indexer_config['SEND_PERIOD'] = 60
    event = threading.Event()
    # add some trash to dir, not a file
    os.makedirs(
        os.path.join(indexer_config['BASE_DIR'], 'foobar.log'), exist_ok=True)
    # add one file with wrong extension
    with open(os.path.join(indexer_config['BASE_DIR'], 'some.txt'), 'tw') as f:
        json.dump({'param': 6}, f)
    # and one busy file
    process = DeferredProcess(indexer_config, 'barfoo')
    process.start()
    try:
        process.ready.wait(60)
        orig_waiter = None
        indexer = None

        def on_wait(t):
            event.set()
            indexer._waiter = orig_waiter

        def send_signal(data, **_):
            if data[0].data['param'] == 1:
                # mock 'waiter.wait' so we can be sure that all deferred queue
                # will be processed
                nonlocal orig_waiter
                orig_waiter = indexer._waiter
                indexer._waiter = mock.MagicMock()
                indexer._waiter.is_set.return_value = False
                indexer._waiter.wait = on_wait

        with indexing.ElasticIndexer(
                indexer_config, autostart=False) as indexer:
            indexer.file_send_signal.connect(send_signal)
            # generate 2 work file (one empty) and 2 deferred file
            # needed 2 files, to be sure that not only one file will
            # be sent
            indexer.index({'param': 0})
            indexer.index({'param': 1})
            indexer.index({'param': 2})
            indexer.start_indexing()
            assert event.wait(60)
    finally:
        process.finish.set()
        process.join(50)
    assert len(indexer.transport.queue) == 3
    assert indexer.transport.queue[0][0].data['param'] == 0
    indexer.transport.queue.sort(key=lambda x: x[0].data['param'])
    assert indexer.transport.queue[1][0].data['param'] == 1
    assert indexer.transport.queue[2][0].data['param'] == 2


def test_deferred_queue_timer(indexer_config):
    indexer_config['PACK_SIZE'] = 1
    indexer_config['FILE_SIZE_LIMIT'] = 1
    indexer_config['SEND_PERIOD'] = 60
    event = threading.Event()
    waiter = mock.MagicMock()
    orig_waiter = None
    indexer = None
    more_index = [{'param': 3}]

    def on_wait(t):
        event.set()
        waiter.timing = t
        indexer._waiter = orig_waiter
        indexer._stop_indexing = True

    def send_signal(data, **_):
        if data[0].data['param'] == 0:
            # mock 'waiter.wait' so we can be sure that all deferred queue
            # will be processed
            nonlocal orig_waiter
            orig_waiter = indexer._waiter
            indexer._waiter = waiter
            indexer._waiter.is_set.return_value = False
            indexer._waiter.wait = on_wait
            # make timer exprired, only one defered file should be sent
            indexer.send_period = 0
        else:
            if more_index:
                # first deferred send
                # write directly to working file so waiter trigger is not set
                # to check just timer
                indexer._work_files[-1].write_data(more_index.pop(0))
            else:
                # get timer back
                indexer.send_period = 60

    with indexing.ElasticIndexer(indexer_config, autostart=False) as indexer:
        indexer.file_send_signal.connect(send_signal)
        # generate 2 work file (one empty) and 2 deferred file
        indexer.index({'param': 0})
        indexer.index({'param': 1})
        indexer.index({'param': 2})
        indexer.start_indexing()
        assert event.wait(60)
    # all data is sent but order - 1 current, 1 deferred, 1 current, 1 def
    assert len(indexer.transport.queue) == 4
    assert indexer.transport.queue[0][0].data['param'] == 0
    assert indexer.transport.queue[1][0].data['param'] != 0
    assert indexer.transport.queue[2][0].data['param'] == 3
    assert waiter.timing > 50


class InitFailingTransport(transport.TestTransport):
    init_calls = 0

    def init_indexing(self):
        self.init_calls += 1
        if self.init_calls == 1:
            self.queue.append('init failed')
            raise ValueError()
        self.queue.append('init success')


def test_retry_init(indexer_config):
    indexer_config['PACK_SIZE'] = 1
    indexer_config['FILE_SIZE_LIMIT'] = 1
    indexer_config['transport'] = InitFailingTransport
    event = threading.Event()

    def send_signal(data, **_):
        if data[0].data['param'] == 1:
            # deferred send
            indexer.index({'param': 2})
        elif data[0].data['param'] == 2:
            event.set()

    with indexing.ElasticIndexer(indexer_config, autostart=False) as indexer:
        indexer.file_send_signal.connect(send_signal)
        indexer.index({'param': 0})
        indexer.index({'param': 1})
        with mock.patch.object(indexing.logger, 'exception') as error_mock:
            indexer.start_indexing()
            assert event.wait(60)
    assert error_mock.called
    assert len(indexer.transport.queue) == 5
    assert indexer.transport.queue[0] == 'init failed'
    assert indexer.transport.queue[1] == 'init success'
    assert indexer.transport.queue[2][0].data['param'] == 0
