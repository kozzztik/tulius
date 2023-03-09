import threading

from django.db import utils


class ConnectionHandler(utils.ConnectionHandler):
    def __init__(self, settings=None):
        super().__init__(settings)
        self._connection_pools = {}
        self._lock = threading.Lock()

    def __getitem__(self, alias):
        try:
            return getattr(self._connections, alias)
        except AttributeError as exc:
            if alias not in self.settings:
                raise self.exception_class(
                    f"The connection '{alias}' doesn't exist."
                ) from exc
        with self._lock:
            pool = self._connection_pools.setdefault(alias, [])
            if pool:
                conn = pool.pop()
            else:
                conn = self.create_connection(alias)
                conn.inc_thread_sharing()  # be thread free
        setattr(self._connections, alias, conn)
        return conn

    def close_context(self):
        with self._lock:
            for alias in self:
                if hasattr(self._connections, alias):
                    conn = getattr(self._connections, alias)
                    delattr(self._connections, alias)
                    pool = self._connection_pools.setdefault(alias, [])
                    pool.append(conn)
