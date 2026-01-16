import os
import threading
import uuid
import datetime
import logging
import random
import time
import signal

from django.conf import settings
from django.core import signals
from django.utils import module_loading

from tulius.core.elastic import files
from tulius.core.elastic import transport

logger = logging.getLogger('deferred_indexing')


class ClosedException(Exception):
    pass


class ElasticIndexer:
    _thread = None
    _stop_indexing = False

    def __init__(self, config, autostart=True):
        self.config = config.copy()
        self.send_period = self.config.get('SEND_PERIOD', 15)
        self.pack_size = self.config.get('PACK_SIZE', 1000)
        self.file_size_limit = self.config.get(
            'FILE_SIZE_LIMIT', 1024 * 1024 * 50)
        self._closing = False
        self._transport_cls = self.config.get('transport', transport.ElasticTransport)
        if isinstance(self._transport_cls, str):
            self._transport_cls = module_loading.import_string(self._transport_cls)
        self._base_dir = self.config['BASE_DIR']
        os.makedirs(self._base_dir, exist_ok=True)
        self.dead_queue_dir = self.config.setdefault(
            'DEAD_QUEUE_DIR', os.path.join(self._base_dir, 'dead'))
        os.makedirs(self.dead_queue_dir, exist_ok=True)
        self.file_send_signal = signals.Signal()
        self.autostart = autostart
        self._init()

    def _init(self):
        self.pid = os.getpid()
        self.transport: transport.BaseTransport | None =  self._transport_cls(self.config)
        self._lock = threading.Lock()
        self._work_files = []
        self._waiter = threading.Event()
        self._dead_queue_file = None
        self._thread = None
        self._stop_indexing = False
        if self.autostart:
            self.start_indexing()

    def start_indexing(self):
        if not self._thread:
            self._stop_indexing = False
            self._thread = threading.Thread(target=self._run, daemon=True)
            self._thread.start()
        else:
            logger.warning('Indexing already started')

    def stop_indexing(self):
        if self._thread:
            self._stop_indexing = True
            self._waiter.set()
            self._thread.join()
            self._thread = None

    @staticmethod
    def _gen_file_name():
        date = datetime.datetime.now()
        return f'{date.year}_{date.month:02}_{date.day:02}_{uuid.uuid4()}'

    def _write_to_dead_queue(self, exc, data):
        """ should be called under lock"""
        if not self._dead_queue_file:
            self._dead_queue_file = files.DeadQueueFile(
                self.config, self._gen_file_name(), write_caching=False)
        self._dead_queue_file.write_data((exc, data))
        if self._dead_queue_file.size > self.file_size_limit:
            self._dead_queue_file.close()
            self._dead_queue_file = None

    def index(self, data):
        if self._closing:
            raise ClosedException()
        if self.pid != os.getpid():
            # we are in new process (after fork)
            logger.info('Reinit indexing (process changed)')
            self._init()
        with self._lock:
            if not self._work_files:
                self._work_files.append(files.WorkFile(
                    self.config, self._gen_file_name(), write_caching=True))
            self._work_files[-1].write_data(data)
            if len(self._work_files[-1].cache) >= self.pack_size:
                self._waiter.set()
            if self._work_files[-1].size < self.file_size_limit:
                return
            # we got here because current file too big
            if len(self._work_files) > 1:
                # that is not file that is sending now, so just close it
                # but we never close _work_files[0] here
                self._work_files.pop(-1).close()
            else:
                # that is file that is about to send, trigger sending
                self._waiter.set()
            # anyway we need new file with no write caching
            self._work_files.append(files.WorkFile(
                self.config, self._gen_file_name(),
                write_caching=False))

    def _check_ext(self, ext):
        return ext[1:] in [
            self.config.get('DATA_EXT') or 'log',
            self.config.get('CONF_EXT') or 'conf']

    def _get_deferred_file(self):
        queue = [f for f in os.scandir(self._base_dir) if f.is_file()]
        while queue:
            f = queue.pop(random.randrange(0, len(queue)))
            try:
                name, ext = os.path.splitext(f.name)
                if not self._check_ext(ext):
                    continue
                with self._lock:
                    if [w for w in self._work_files if w.name == name]:
                        continue
                return files.WorkFile(self.config, name)
            except OSError:
                pass

    def _push_deferred_queue(self):
        # until new pack is ready
        start = time.time()
        while not self._waiter.is_set():
            work_file = self._get_deferred_file()
            if not work_file:
                break
            while not self._waiter.is_set() and work_file:
                if not self._send_file(work_file):
                    work_file.remove()
                    work_file = None
                if time.time() - start > self.send_period:
                    # it's time to get back to current file
                    return time.time() - start
        return time.time() - start

    def _send_file(self, work_file: files.WorkFile):
        queue = []
        dead_queue = []
        pack = work_file.read_bulk(self.pack_size)
        if not pack:
            return 0
        for entity in pack:
            if entity.exc:
                dead_queue.append(entity)
            else:
                queue.append(entity)
        if queue:
            self.transport.do_index(queue)
            pack = queue
            queue = []
            for item in pack:
                if item.exc:
                    dead_queue.append(item)
                else:
                    queue.append(item)
        for entity in dead_queue:
            self._write_to_dead_queue(entity.exc, entity.data)
        # commit
        work_file.data_sent(pack[-1].end_pos)
        logger.debug('File send %s - pos %s', work_file.name, pack[-1].end_pos)
        self.file_send_signal.send(
            sender=self, work_file=work_file, data=queue, errors=dead_queue)
        return len(pack)

    def push_dead_queue(self):
        logger.warning('Pushing dead queue')
        processed = set()
        for f in os.scandir(self.dead_queue_dir):
            if not f.is_file():
                continue
            name, ext = os.path.splitext(f.name)
            if not self._check_ext(ext):
                continue
            if name in processed:
                continue
            try:
                work_file = files.DeadQueueFile(self.config, name)
            except OSError:
                processed.add(name)
                logger.error('File is busy %s', f.name)
                continue
            while True:
                if not self._send_file(work_file):
                    break
            logger.warning('File is send %s', f.name)
            work_file.remove()
            processed.add(name)
            logger.warning('File is removed from dead queue %s', f.name)
        logger.warning('Dead queue processing finished.')

    def _send_working_files(self):
        while True:
            if self._stop_indexing:
                return
            if not self._work_files:
                break
            sending_file: files.WorkFile = self._work_files[0]
            # if we send not current file, send it until it ends
            while True:
                self._send_file(sending_file)
                with self._lock:
                    # read more under lock
                    pack = self._work_files[0].read_bulk(self.pack_size)
                    if len(self._work_files) > 1:
                        # if we send not current file, stop only it is
                        # empty, then remove it
                        if not pack:
                            self._work_files.pop(0).remove()
                            self._work_files[0].write_caching = True
                            break
                    else:
                        # if we send current file stop if there are no
                        # full pack to send
                        if len(pack) < self.pack_size:
                            if not self._stop_indexing:
                                # if stop indexing was called after triggering
                                # new send this will drop flag that makes stop
                                self._waiter.clear()
                            return

    def _run(self):
        transport_inited = False
        logger.warning('Indexing started pid %s', os.getpid())
        while True:
            try:
                if self._stop_indexing:
                    return
                if not transport_inited:
                    self.transport.init_indexing()
                    transport_inited = True
                self._send_working_files()
                # until new pack is ready send data in other files in queue
                wait_time = self.send_period - self._push_deferred_queue()
                if wait_time > 0:
                    self._waiter.wait(wait_time)
            except transport.TransportNotReady as exc:
                logging.warning(exc)
                time.sleep(self.send_period)
            except Exception as e:
                logger.exception(e)

    def close(self):
        with self._lock:
            if self._closing:
                return
            self._closing = True
        self.stop_indexing()
        with self._lock:
            while self._work_files:
                self._work_files.pop(0).close()
            if self._dead_queue_file:
                self._dead_queue_file.close()
                self._dead_queue_file = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


_indexer: ElasticIndexer | None = None


def get_indexer() -> ElasticIndexer:
    global _indexer  # pylint: disable=global-statement
    if not _indexer:
        _indexer = ElasticIndexer(
            getattr(settings, 'ELASTIC_INDEXING', None) or {})
    return _indexer


def close(*_):
    global _indexer  # pylint: disable=global-statement
    if _indexer:
        _indexer.close()
    _indexer = None


signal.signal(signal.SIGINT, close)
signal.signal(signal.SIGTERM, close)
