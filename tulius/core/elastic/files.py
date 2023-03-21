import json
import os
import threading

from django.core.serializers import json as dj_json


class Entity:
    def __init__(self, start_pos, end_pos, data):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.data = data

    @classmethod
    def read(cls, fd):
        data = fd.readline()
        return json.loads(data)

    @classmethod
    def write(cls, fd, data):
        # TODO escaping \n?
        fd.write(
            json.dumps(data, cls=dj_json.DjangoJSONEncoder).encode('utf-8'))
        fd.write(b'\n')


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
            lock_file(self._data_fd)
            self._locked = True
        except OSError:
            self.close()
            raise
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
            start_pos = self._data_fd.tell()
            self.entity_cls.write(self._data_fd, data)
            self.size = self._data_fd.tell()
            entity = self.entity_cls(start_pos, self.size, data)
            self._data_fd.flush()
            if not self.write_caching:
                return
            if len(self.cache) < self._cache_limit:
                return
            if self.cache:
                cache_end = self.cache[-1].end_pos
            else:
                cache_end = self._send_position
            if cache_end != start_pos:
                # for some reason cache have missed some values, keep it
                # consistent
                return
            self.cache.append(entity)

    def read_bulk(self, count):
        with self._lock:
            while len(self.cache) < count:
                if self.cache:
                    start_pos = self.cache[-1].end_pos
                else:
                    start_pos = self._send_position
                if start_pos >= self.size:
                    break
                self._data_fd.seek(start_pos, 0)
                data = self.entity_cls.read(self._data_fd)
                self.cache.append(
                    self.entity_cls(start_pos, self._data_fd.tell(), data))
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
                    self.unlock_file(self._data_fd)
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
    @classmethod
    def read(cls, fd):
        while True:
            data = fd.readline()
            if data.startswith('#'):
                continue
        return json.loads(data)

    @classmethod
    def write(cls, fd, data):
        error_lines = [
            ('# ' + line).encode('utf-8') for line in str(data[0]).split('\n')]
        fd.writelines(error_lines)
        super().write(fd, data[1])


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
