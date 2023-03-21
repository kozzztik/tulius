import os
import threading
import uuid
import datetime
import logging
import random
import shutil
import time
import signal

import elasticsearch8
from django.conf import settings
from django.core import signals
from django.core import exceptions
from django.utils import module_loading

from tulius.core.elastic import files

logger = logging.getLogger(__name__)


class FormatException(Exception):
    pass


class ClosedException(Exception):
    pass


class ElasticIndexer:
    def __init__(self, config):
        self.config = config.copy()
        self.send_period = self.config.get('SEND_PERIOD', 15)
        self.pack_size = self.config.get('PACK_SIZE', 1000)
        self.timeout = self.config.get('TIMEOUT', 60)
        self.file_size_limit = self.config.get(
            'FILE_SIZE_LIMIT', 1024 * 1024 * 50)
        self._closing = False
        self.client = elasticsearch8.Elasticsearch(
            hosts=settings.ELASTIC_HOSTS, request_timeout=self.timeout)
        self._base_dir = self.config['BASE_DIR']
        os.makedirs(self._base_dir, exist_ok=True)
        self._dead_queue_dir = self.config.setdefault(
            'DEAD_QUEUE_DIR', os.path.join(self._base_dir, 'dead'))
        os.makedirs(self._dead_queue_dir, exist_ok=True)
        self._lock = threading.Lock()
        self._waiter = threading.Event()
        self._current_file = None
        self._sending_file = None
        self._dead_queue_file = None
        self._thread = threading.Thread(target=self._run)
        self._thread.start()
        self.file_send_signal = signals.Signal()

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
        with self._lock:
            if not self._current_file:
                self._current_file = files.WorkFile(
                    self.config, self._gen_file_name(),
                    write_caching=not self._sending_file)
            self._current_file.write_data(data)
            if len(self._current_file.cache) >= self.pack_size:
                self._waiter.set()
            if self._current_file.size < self.file_size_limit:
                return
            # file too big, need to close. But first - need to send it
            if self._sending_file is None:
                self._sending_file = self._current_file
                self._waiter.set()
            else:
                # previous file is still in work, just close current one
                self._current_file.close()
            self._current_file = None

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
                if self._current_file and name == self._current_file.name:
                    continue
                if self._sending_file and name == self._sending_file.name:
                    continue
                return files.WorkFile(self.config, name)
            except OSError:
                pass
            except FormatException:
                shutil.move(f.path, os.path.join(self._dead_queue_dir, f.name))

    def _push_deferred_queue(self):
        # until new pack is ready
        start = time.time()
        while not self._waiter.is_set():
            work_file = self._get_deferred_file()
            if not work_file:
                break
            while not self._waiter.is_set():
                if not self._send_file(work_file):
                    work_file.remove()
                if time.time() - start > self.send_period:
                    # it's time to get back to current file
                    return time.time() - start
        return time.time() - start

    def _send_file(self, work_file: files.WorkFile):
        operations = []
        queue = work_file.read_bulk(self.pack_size)
        if not queue:
            # TODO case where no data in file, but there is more size
            return 0
        for entity in queue:
            doc = entity.data.copy()
            # TODO case where no index in doc
            operations.append({
                doc.pop('_action', 'index'): {
                    '_index': doc.pop('_index', 'noindex'),
                    '_id': doc.pop('_id', None)
                }
            })
            operations.append(doc)
        response = self.client.bulk(operations=operations, refresh=False)
        if response['errors']:
            for i, item in enumerate(response['items']):
                item = list(item.values())[0]
                if item['status'] == 200:
                    continue
                self._write_to_dead_queue(item.get('error'), queue[i].data)
        work_file.data_sent(queue[-1].end_pos)
        logger.debug('File send', extra={'file_name': work_file.name})
        self.file_send_signal.send(
            sender=self, work_file=work_file, errors=response['errors'])
        return len(queue)

    def push_dead_queue(self):
        logger.warning('Pushing dead queue')
        for f in os.scandir(self._dead_queue_dir):
            if not f.is_file:
                continue
            name, ext = os.path.splitext(f.name)
            if not self._check_ext(ext):
                continue
            try:
                work_file = files.DeadQueueFile(self.config, name)
            except OSError:
                logger.error('File is busy %s', f.name)
                continue
            except FormatException:
                logger.error('File is broken %s', f.name)
                continue
            while True:
                if not self._send_file(work_file):
                    break
            logger.warning('File is send %s', f.name)
            work_file.remove()
            logger.warning('File is removed from dead queue %s', f.name)
        logger.warning('Dead queue processing finished.')

    def put_index_templates(self):
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
                self.client.indices.put_index_template(name=name, **template)
            except Exception as exc:
                logger.error('Failed to install template %s: %s', name, exc)

    def _run(self):
        try:
            self.put_index_templates()
        except Exception as exc:
            logger.exception('Failed to install index templates: %s', exc)
        while True:
            try:
                if self._closing:
                    return
                if self._sending_file:
                    # if we send not current file, send it until it ends
                    while True:
                        if not self._send_file(self._sending_file):
                            break
                    with self._lock:
                        self._sending_file.remove()
                        self._sending_file = None
                # send it at least once as we got here
                if self._current_file:
                    self._send_file(self._current_file)
                    while True:
                        # send more if there is one more full pack
                        with self._lock:
                            pack = self._current_file.read_bulk(self.pack_size)
                            if len(pack) < self.pack_size:
                                self._waiter.clear()
                                break
                        self._send_file(self._current_file)
                # until new pack is ready send data in other files in queue
                wait_time = self.send_period - self._push_deferred_queue()
                if wait_time > 0:
                    self._waiter.wait(wait_time)
            except elasticsearch8.ConnectionError as exc:
                logging.warning(exc)
                time.sleep(self.send_period)
            except Exception as e:
                logger.exception(e)

    def close(self):
        if self._closing:
            return
        self._closing = True
        self._waiter.set()
        self._thread.join()
        with self._lock:
            if self._sending_file:
                self._send_file(self._sending_file)
                self._sending_file.close()
                self._sending_file = None
            if self._current_file:
                self._send_file(self._current_file)
                self._current_file.close()
                self._current_file = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


_indexer = None


def get_indexer() -> ElasticIndexer:
    global _indexer
    if not _indexer:
        _indexer = ElasticIndexer(
            getattr(settings, 'ELASTIC_INDEXING', None) or {})
    return _indexer


def _close_indexer(*args):
    global _indexer
    if _indexer:
        _indexer.close()
    _indexer = None

signal.signal(signal.SIGINT, _close_indexer)
signal.signal(signal.SIGTERM, _close_indexer)
