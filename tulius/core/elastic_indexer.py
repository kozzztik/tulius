import traceback
import os
import decimal
import threading
import uuid
import datetime
import json
import logging
import random
import shutil
import time

import elasticsearch8
from django.conf import settings
from django.core import signals
from django.core import exceptions
from django.core.serializers import json as dj_json
from django.utils import module_loading
from django.utils import functional

logger = logging.getLogger(__name__)


class FormatException(Exception):
    pass


class ClosedException(Exception):
    pass


class WorkFile:
    def __init__(self, path, mode='a'):
        self.path = path
        # pylint: disable=consider-using-with
        self.fd = open(path, mode, encoding='utf-8')
        self._locked = False
        self.queue = []
        try:
            # Posix based file locking (Linux, Ubuntu, MacOS, etc.)
            # pylint: disable=import-outside-toplevel
            import fcntl

            def lock_file(f):
                fcntl.lockf(f, fcntl.LOCK_EX)

            def unlock_file(f):
                fcntl.lockf(f, fcntl.LOCK_UN)
        except ModuleNotFoundError:
            # Windows file locking
            # pylint: disable=import-outside-toplevel
            import msvcrt

            def file_size(f):
                return os.path.getsize(os.path.realpath(f.name))

            def lock_file(f):
                msvcrt.locking(f.fileno(), msvcrt.LK_RLCK, file_size(f))

            def unlock_file(f):
                msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, file_size(f))
        self.unlock_file = unlock_file
        try:
            lock_file(self.fd)
            self._locked = True
        except OSError:
            self.close()
            raise

    def close(self):
        try:
            if self._locked:
                self.unlock_file(self.fd)
            self._locked = False
        except OSError:
            pass
        self.fd.close()
        self.fd = None

    def remove(self):
        self.fd.truncate(0)
        self.close()
        try:
            os.remove(self.path)
        except PermissionError:
            # someone took file to delete after we closed it.
            pass


class QueueFile(WorkFile):
    def __init__(self, path):
        super().__init__(path, 'r+')
        try:
            self.queue = [json.loads(line) for line in self.fd]
        except Exception as exc:
            self.close()
            raise FormatException() from exc


class DeadQueueFile(WorkFile):
    def __init__(self, path):
        super().__init__(path, 'r+')
        try:
            for line in self.fd:
                if line.startswith('#'):
                    continue
                self.queue.append(json.loads(line))
        except Exception as exc:
            self.close()
            raise FormatException() from exc


class ElasticIndexer:
    def __init__(self, config):
        self.config = config
        self.send_period = self.config.get('SEND_PERIOD', 15)
        self.pack_size = self.config.get('PACK_SIZE', 1000)
        self.timeout = self.config.get('TIMEOUT', 60)
        self._closing = False
        self.client = elasticsearch8.Elasticsearch(
            hosts=settings.ELASTIC_HOSTS, request_timeout=self.timeout)
        self.base_dir = self.config['BASE_DIR']
        os.makedirs(self.base_dir, exist_ok=True)
        self.dead_queue = os.path.join(self.base_dir, 'dead')
        os.makedirs(self.dead_queue, exist_ok=True)
        self._lock = threading.Lock()
        self._waiter = threading.Event()
        self._current_file = None
        self._sending_file = None
        self._thread = threading.Thread(target=self._run)
        self._thread.start()
        self.file_send_signal = signals.Signal()

    @staticmethod
    def _gen_file_name(base):
        date = datetime.datetime.now()
        return os.path.join(
            base,
            f'{date.year}_{date.month:02}_{date.day:02}_'
            f'{os.getpid()}_{uuid.uuid4()}')

    def _open_file(self):
        self._current_file = WorkFile(self._gen_file_name(self.base_dir), 'a')

    def _rotate_file(self):
        if self._current_file is None:
            return
        if not self._current_file.queue:
            return
        if self._sending_file is None:
            self._sending_file = self._current_file
            self._waiter.set()
        else:
            self._current_file.close()
        self._open_file()

    def index(self, data):
        if self._closing:
            raise ClosedException()
        raw_data = json.dumps(data, cls=dj_json.DjangoJSONEncoder)
        raw_data = raw_data.replace('\n', r'\n') + '\n'
        with self._lock:
            if not self._current_file:
                self._open_file()
            self._current_file.queue.append(data)
            self._current_file.fd.write(raw_data)
            self._current_file.fd.flush()
            if len(self._current_file.queue) >= self.pack_size:
                self._rotate_file()

    def _push_queue(self):
        queue = [f for f in os.scandir(self.base_dir) if f.is_file()]
        while queue:
            f = queue.pop(random.randrange(0, len(queue)))
            try:
                queue_file = QueueFile(f.path)
                if queue_file.queue:
                    self._sending_file = queue_file
                    return len(queue)
                queue_file.remove()
            except OSError:
                pass
            except FormatException:
                shutil.move(f.path, os.path.join(self.dead_queue, f.name))

    def _send_file(self, work_file: WorkFile):
        operations = []
        for doc in work_file.queue:
            doc = doc.copy()
            # TODO case where no index in doc
            operations.append({
                doc.pop('_action', 'index'): {
                    '_index': doc.pop('_index', 'noindex'),
                    '_id': doc.pop('_id', None)
                }
            })
            operations.append(doc)
        if not operations:
            return
        response = self.client.bulk(operations=operations, refresh=False)
        if response['errors']:
            with open(
                    self._gen_file_name(self.dead_queue), 'a', encoding='utf-8'
            ) as f:
                for i, item in enumerate(response['items']):
                    item = list(item.values())[0]
                    if item['status'] == 200:
                        continue
                    error_line = '# ' + str(
                        item.get('error')).replace('\n', r'\n') + '\n'
                    f.write(error_line)
                    f.write(json.dumps(
                        work_file.queue[i], cls=dj_json.DjangoJSONEncoder
                    ) + '\n')
        logger.debug('File send', extra={'file_name': work_file.path})
        self.file_send_signal.send(
            sender=self, work_file=work_file, errors=response['errors'])

    def push_dead_queue(self):
        logger.warning('Pushing dead queue')
        for f in os.scandir(self.dead_queue):
            if not f.is_file:
                continue
            try:
                work_file = DeadQueueFile(f.path)
            except OSError:
                logger.error('File is busy %s', f.name)
                continue
            except FormatException:
                logger.error('File is broken %s', f.name)
                continue
            self._send_file(work_file)
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
                more_queue = 0
                with self._lock:
                    if self._sending_file is None:
                        more_queue = self._push_queue()
                    if self._sending_file is None:
                        self._rotate_file()
                if self._sending_file:
                    self._send_file(self._sending_file)
                    with self._lock:
                        if self._sending_file.fd:
                            self._sending_file.remove()
                        self._sending_file = None
                if not more_queue:
                    self._waiter.wait(self.send_period)
                    self._waiter.clear()
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
                if self._sending_file.fd:
                    self._sending_file.remove()
                self._sending_file = None
            if self._current_file:
                self._send_file(self._current_file)
                if self._current_file.fd:
                    self._current_file.remove()
                self._current_file = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


indexer = ElasticIndexer(getattr(settings, 'ELASTIC_INDEXING', None) or {})


class Handler(logging.Handler):
    def __init__(self, index_name=None, level=logging.NOTSET):
        self._index_name = index_name or '{logger}'
        super().__init__(level=level)

    def get_index_name(self, tstamp, record):
        return self._index_name.format(
            logger=record.name, year=tstamp.year, month=tstamp.month,
            day=tstamp.day
        )

    def emit(self, record: logging.LogRecord) -> None:
        tstamp = datetime.datetime.utcfromtimestamp(record.created)
        message = {
            '_action': 'index',
            '_index': self.get_index_name(tstamp, record),
            '_id': str(uuid.uuid4()),
            '@timestamp': tstamp,
            'message': record.getMessage(),
            'level': record.levelname,
            'logger_name': record.name,
        }
        message.update(self.get_extra_fields(record))
        if record.exc_info:
            message.update(self.get_debug_fields(record))
        indexer.index(message)

    @staticmethod
    def get_extra_fields(record):
        # The list contains all the attributes listed in
        # http://docs.python.org/library/logging.html#logrecord-attributes
        skip_list = (
            'args', 'asctime', 'created', 'exc_info', 'exc_text', 'filename',
            'funcName', 'id', 'levelname', 'levelno', 'lineno', 'module',
            'msecs', 'msecs', 'message', 'msg', 'name', 'pathname', 'process',
            'processName', 'relativeCreated', 'thread', 'threadName', 'extra',
            'stack_info')

        easy_types = (
            str, bool, dict, float, int, list, type(None),
            datetime.datetime, datetime.date, datetime.time,
            datetime.timedelta, decimal.Decimal, uuid.UUID, functional.Promise
        )

        fields = {}

        for key, value in record.__dict__.items():
            if key not in skip_list:
                if isinstance(value, easy_types):
                    fields[key] = value
                else:
                    fields[key] = repr(value)

        return fields

    @staticmethod
    def get_debug_fields(record):
        fields = {
            'lineno': record.lineno,
            'process': record.process,
            'thread_name': record.threadName,
        }
        if record.exc_info:
            fields['stack_trace'] = ''.join(
                traceback.format_exception(*record.exc_info))

        if not getattr(record, 'funcName', None):
            fields['funcName'] = record.funcName

        if not getattr(record, 'processName', None):
            fields['processName'] = record.processName

        return fields
