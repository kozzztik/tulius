import threading
import functools

from asgiref.local import Local

from django import db
from django.db import utils


class ConnectionHandler(utils.ConnectionHandler):
    def __init__(self, settings=None):
        super().__init__(settings)
        self._connection_pools = {}
        self._lock = threading.Lock()

    @classmethod
    def monkey_patch(cls):
        """
        Django db connections does not really support asgi, so it doesn't
        correctly close connections and have no support of connection pools
        needed for async.

        We patch connections object in place, as it can be already imported
        somewhere.
        """
        if getattr(db.connections, '_lock', None):
            return
        db.connections._connection_pools = {}
        db.connections._lock = threading.Lock()
        db.connections._connections = Local(False)
        old_cls = db.connections.__class__
        old_cls.__getitem__ = cls.__getitem__
        old_cls.close_context = cls.close_context
        old_cls.close_old_connections = cls.close_old_connections
        db.connections.close_all = functools.partial(
            cls.close_all, db.connections)

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
            conn = None
            while pool:
                conn = pool.pop()
                conn.close_if_unusable_or_obsolete()
                if conn.connection:
                    break
                conn = None
            if conn is None:
                conn = self.create_connection(alias)
                conn.inc_thread_sharing()  # be thread free
        setattr(self._connections, alias, conn)
        return conn

    def close_old_connections(self, **kwargs):
        with self._lock:
            for alias in self:
                new_pool = []
                pool = self._connection_pools.get(alias, [])
                for conn in pool:
                    conn.close_if_unusable_or_obsolete()
                    if conn.health_check_done:
                        new_pool.append(conn)
                self._connection_pools[alias] = new_pool

    def close_context(self):
        with self._lock:
            for alias in self:
                if hasattr(self._connections, alias):
                    conn = getattr(self._connections, alias)
                    delattr(self._connections, alias)
                    pool = self._connection_pools.setdefault(alias, [])
                    pool.append(conn)

    def close_all(self):
        # not super because of monkey patching
        utils.ConnectionHandler.close_all(self)
        for alias in self:
            pool = self._connection_pools.get(alias, [])
            while pool:
                conn = pool.pop()
                conn.close()
