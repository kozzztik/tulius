import json
import os
import threading

import portalocker
from django.core.serializers import json as dj_json


class FileFormatError(Exception):
    pass


class Entity:
    def __init__(self, start_pos, end_pos, data, exc):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.data = data
        self.exc = exc

    @classmethod
    def read(cls, fd):
        start_pos = fd.tell()
        exc = None
        data = fd.readline()
        try:
            data = json.loads(data)
        except ValueError as json_exc:
            if data.endswith(b'\n'):
                # if failed to parse, dont include trailing sep in data
                data = data[:-1]
            exc = json_exc
        return cls(start_pos, fd.tell(), data, exc)

    @classmethod
    def write(cls, fd, data):
        start_pos = fd.tell()
        raw_data = data
        if isinstance(raw_data, bytes):
            raw_data = raw_data.replace(b'\n', rb'\n')
        else:
            raw_data = json.dumps(raw_data, cls=dj_json.DjangoJSONEncoder)
            raw_data = raw_data.replace('\n', r'\n').encode('utf-8')
        # TODO escaping test
        fd.write(raw_data)
        fd.write(b'\n')
        return cls(start_pos, fd.tell(), data, None)


class WorkFile:
    entity_cls = Entity

    def __init__(self, config, name, write_caching=True):
        self.config = config
        self.name = name
        self.write_caching = write_caching
        self.path = os.path.join(self._get_folder(), name)
        # pylint: disable=consider-using-with
        self._locked = False
        self._send_position = 0
        self._lock = threading.Lock()
        self._data_fd_name = '.'.join(
            [self.path, self.config.get('DATA_EXT') or 'log'])
        self._config_fd_name = '.'.join(
            [self.path, self.config.get('CONF_EXT') or 'conf'])
        self._data_fd = open(self._data_fd_name, 'a+b')
        self._config_fd = open(self._config_fd_name, 'a+', encoding='utf-8')
        self.cache = []
        self._cache_limit = config.get('CACHE_LIMIT') or 2000
        try:
            portalocker.lock(
                self._data_fd,
                portalocker.LockFlags.EXCLUSIVE
                + portalocker.LockFlags.NON_BLOCKING)
            self._locked = True
        except portalocker.exceptions.LockException as exc:
            self.close()
            raise OSError() from exc
        self._read_config()
        self.size = self._data_fd.seek(0, 2)

    def _get_folder(self):
        return self.config.get('BASE_DIR') or os.path.curdir

    def _read_config(self):
        self._config_fd.seek(0, 0)
        data = self._config_fd.readline()
        try:
            self._send_position = int(data.strip())
        except ValueError:
            self._send_position = 0
        except Exception:
            # TODO correct exception
            self._send_position = 0

    def _update_config(self):
        self._config_fd.truncate(0)
        self._config_fd.seek(0, 0)
        self._config_fd.write(str(self._send_position))
        self._config_fd.flush()

    def write_data(self, data):
        with self._lock:
            # move to end of file
            self._data_fd.seek(0, 2)
            entity = self.entity_cls.write(self._data_fd, data)
            self.size = entity.end_pos
            self._data_fd.flush()
            if not self.write_caching:
                return
            if len(self.cache) >= self._cache_limit:
                return  # todo test caching works
            if self.cache:
                cache_end = self.cache[-1].end_pos
            else:
                cache_end = self._send_position
            if cache_end != entity.start_pos:
                # for some reason cache have missed some values, keep it
                # consistent
                return
            self.cache.append(entity)

    def read_bulk(self, count):
        with self._lock:
            if len(self.cache) < count:
                if self.cache:
                    start_pos = self.cache[-1].end_pos
                else:
                    start_pos = self._send_position
                self._data_fd.seek(start_pos, 0)
            while len(self.cache) < count:
                if self._data_fd.tell() >= self.size:
                    break  # TODO test that no infinite read
                self.cache.append(self.entity_cls.read(self._data_fd))
            return self.cache[:count]

    def data_sent(self, position):
        with self._lock:
            self._send_position = position
            self.cache = [e for e in self.cache if e.end_pos > position]
            self._update_config()

    def close(self):
        with self._lock:
            try:
                if self._locked:
                    portalocker.unlock(self._data_fd)
                self._locked = False
            except OSError:
                pass
            self._data_fd.close()
            self._data_fd = None
            self._config_fd.close()
            self._config_fd = None

    def remove(self):
        # TODO add close_or_remove
        with self._lock:
            self._data_fd.truncate(0)
            self._data_fd.flush()
            self.size = 0
            self._send_position = 0
        self.close()
        try:
            os.remove(self._data_fd_name)
            os.remove(self._config_fd_name)
        except PermissionError:
            # someone took file to delete after we closed it.
            pass


class DeadQueueEntity(Entity):
    def __init__(self, start_pos, end_pos, data, exc):
        super().__init__(start_pos, end_pos, data, exc)
        self.orig_exc = None

    @classmethod
    def read(cls, fd):
        exc = None
        orig_exc = []
        start_pos = fd.tell()
        while True:
            data = fd.readline()
            if data.startswith(b'#'):
                orig_exc.append(data.decode('utf-8'))
                continue
            try:
                data = json.loads(data)
            except ValueError as json_exc:
                exc = json_exc
            entity = cls(start_pos, fd.tell(), data, exc)
            entity.orig_exc = ''.join(orig_exc)
            return entity

    @classmethod
    def write(cls, fd, data):
        start_pos = fd.tell()
        error_lines = [
            ('# ' + line + '\n').encode('utf-8')
            for line in str(data[0]).split('\n')]
        fd.writelines(error_lines)
        entity = super().write(fd, data[1])
        entity.start_pos = start_pos
        return entity


class DeadQueueFile(WorkFile):
    entity_cls = DeadQueueEntity

    def _get_folder(self):
        return self.config.get('DEAD_QUEUE_DIR')

    def _read_config(self):
        # TODO
        self._config_fd.seek(0, 0)
        data = self._config_fd.readline()
        try:
            self._send_position = int(data.strip())
        except ValueError:
            self._send_position = 0
        except Exception:
            # TODO correct exception
            self._send_position = 0

    def _update_config(self):
        # TODO
        self._config_fd.truncate(0)
        self._config_fd.seek(0, 0)
        self._config_fd.write(str(self._send_position))
        self._config_fd.flush()
