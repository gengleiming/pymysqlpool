from threading import Condition

from .connection import Connection


class PoolError(Exception):
    pass


class InvalidConnection(PoolError):
    pass


class TooManyConnections(PoolError):
    pass


class DBPool:
    def __init__(self, max_connections=0, set_session=None, reset=True, ping=1, *args, **kwargs):
        """

        :param max_connections: max connections in pool
        :param set_session: init sql for session
        :param reset: False or None to rollback transcations started with begin(),
        True to always issue a rollback for safety's sake
        :param failures:
        :param ping: check connection with ping() on every request
        :param args:
        :param kwargs:
        """
        self._args, self._kwargs = args, kwargs
        self._set_session = set_session
        self._reset = reset
        self._ping = ping

        if max_connections:
            self._max_connections = max_connections
        else:
            self._max_connections = 0

        # idle cache for connections
        self._idle_cache = []
        self._lock = Condition()
        self._connections = 0

    def _connection(self):
        return Connection(self._set_session, self._ping, *self._args, **self._kwargs)

    def connect(self):
        with self._lock:
            while self._max_connections and self._connections >= self._max_connections:
                self._wait_lock()
            if not self._idle_cache:
                con = self._connection()
            else:
                con = self._idle_cache.pop(0)
                con.ping_check()

            con = WorkConnection(self, con)
            self._connections += 1
        return con

    def cache(self, con):
        with self._lock:
            con.reset(force=self._reset)
            self._idle_cache.append(con)
            self._connections -= 1
            self._lock.notify()

    def close(self):
        with self._lock:
            while self._idle_cache:
                con = self._idle_cache.pop(0)
                con.close()

            self._lock.notifyAll()

    def __del__(self):
        try:
            self.close()
        except:
            pass

    def _wait_lock(self):
        self._lock.wait()


class WorkConnection:

    def __init__(self, pool, con):
        self._pool = pool
        self._con = con

    def close(self):
        if self._con:
            self._pool.cache(self._con)
            self._con = None

    def __getattr__(self, name):
        if self._con:
            return getattr(self._con, name)
        else:
            raise InvalidConnection

    def __del__(self):
        try:
            self.close()
        except:
            pass
