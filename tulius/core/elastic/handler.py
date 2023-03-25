import logging
import datetime
import traceback
import uuid
import decimal

from django.utils import functional

from tulius.core.elastic import indexing


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
        indexing.get_indexer().index(message)

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
