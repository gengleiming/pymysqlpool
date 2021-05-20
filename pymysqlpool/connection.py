import pymysql


class SteadyDBError(Exception):
    pass


class InvalidCursor(SteadyDBError):
    pass


class Connection:
    def __init__(self, set_session=None, ping=1, *args, **kwargs):
        self._con = None
        self._closed = True
        self._transaction = False

        self._set_session_sql = set_session
        self._failures = (pymysql.OperationalError, pymysql.InternalError)
        self._ping = ping if isinstance(ping, int) else 0
        self._args, self._kwargs = args, kwargs
        self.store(self._create())

    def __enter__(self):
        return self

    def __exit__(self, err_type, err_content, err_trace):
        if err_type is None and err_content is None and err_trace is None:
            self.commit()
        else:
            self.rollback()

    def _create(self):
        con = pymysql.connect(*self._args, **self._kwargs)
        try:
            self._set_session(con)
        except Exception as error:
            try:
                con.close()
            except Exception:
                pass
            raise error
        return con

    def _set_session(self, con=None):
        if con is None:
            con = self._con
        if self._set_session_sql:
            cursor = con.cursor()
            for sql in self._set_session_sql:
                cursor.execute(sql)
            cursor.close()

    def store(self, con):
        self._con = con
        self._transaction = False
        self._closed = False

    def close(self):
        if not self._closed:
            try:
                self._con.close()
            except Exception:
                pass
            self._transaction = False
            self._closed = True

    def reset(self, force=False):
        if not self._closed and (force or self._transaction):
            try:
                self.rollback()
            except Exception:
                pass

    def ping_check(self, reconnect=True):
        if not self._ping:
            return

        try:
            alive = self._con.ping(False)
        except pymysql.err.Error:
            alive = False
        except Exception:
            alive = None
            reconnect = False
        else:
            if alive is None:
                alive = True
            if alive:
                reconnect = False
        if reconnect and not self._transaction:
            try:
                con = self._create()
            except Exception:
                pass
            else:
                self.close()
                self.store(con)
                alive = True
        return alive

    def begin(self, *args, **kwargs):
        self._transaction = True
        self._con.begin(*args, **kwargs)

    def commit(self):
        self._transaction = False
        try:
            self._con.commit()
        except self._failures as error:
            try:
                con = self._create()
            except Exception:
                pass
            else:
                self.close()
                self.store(con)
            raise error

    def rollback(self):
        self._transaction = False
        try:
            self._con.rollback()
        except self._failures as error:
            try:
                con = self._create()
            except Exception:
                pass
            else:
                self.close()
                self.store(con)
            raise error

    def cancel(self):
        self._transaction = False
        try:
            cancel = self._con.cancel
        except AttributeError:
            pass
        else:
            cancel()

    def ping(self, *args, **kwargs):
        return self._con.ping(*args, **kwargs)

    def _cursor(self, *args, **kwargs):
        transaction = self._transaction
        if not transaction:
            self.ping_check()
        try:
            cursor = self._con.cursor(*args, **kwargs)
        except self._failures as error:
            try:
                con = self._create()
            except Exception:
                pass
            else:
                try:
                    cursor = con.cursor(*args, **kwargs)
                except Exception:
                    pass
                else:
                    self.close()
                    self.store(con)
                    if transaction:
                        raise error
                    return cursor
                try:
                    con.close()
                except Exception:
                    pass
            if transaction:
                self._transaction = False
            raise error
        return cursor

    def cursor(self, *args, **kwargs):
        return Cursor(self, *args, **kwargs)

    def __del__(self):
        try:
            self.close()
        except:
            pass


class Cursor:

    def __init__(self, con, *args, **kwargs):
        self._cursor = None
        self._closed = True
        self._con = con
        self._args, self._kwargs = args, kwargs
        try:
            self._cursor = con._cursor(*args, **kwargs)
        except AttributeError:
            raise TypeError("%r is not a SteadyDBConnection." % (con,))
        self._closed = False

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def close(self):
        if not self._closed:
            try:
                self._cursor.close()
            except Exception:
                pass
            self._closed = True

    def execute(self, *args, **kwargs):
        con = self._con
        transaction = con._transaction
        if not transaction:
            con.ping_check()
        try:
            result = self._cursor.execute(*args, **kwargs)
        except con._failures as error:
            if not transaction:
                try:
                    cursor2 = con._cursor(*self._args, **self._kwargs)
                except Exception:
                    pass
                else:
                    try:
                        result = cursor2.execute(*args, **kwargs)
                    except Exception:
                        pass
                    else:
                        self.close()
                        self._cursor = cursor2
                        return result
                    try:
                        cursor2.close()
                    except Exception:
                        pass
            try:
                con2 = con._create()
            except Exception:
                pass
            else:
                try:
                    cursor2 = con2.cursor(*self._args, **self._kwargs)
                except Exception:
                    pass
                else:
                    if transaction:
                        self.close()
                        con.close()
                        con.store(con2)
                        self._cursor = cursor2
                        raise error
                    error2 = None
                    try:
                        result = cursor2.execute(*args, **kwargs)
                    except error.__class__:
                        use2 = False
                        error2 = error
                    except Exception as error:
                        use2 = True
                        error2 = error
                    else:
                        use2 = True
                    if use2:
                        self.close()
                        con.close()
                        con.store(con2)
                        self._cursor = cursor2
                        if error2:
                            raise error2
                        return result
                    try:
                        cursor2.close()
                    except Exception:
                        pass
                try:
                    con2.close()
                except Exception:
                    pass
            if transaction:
                self._transaction = False
            raise error
        else:
            return result

    def __getattr__(self, name):
        if self._cursor:
            return getattr(self._cursor, name)
        else:
            raise InvalidCursor

    def __del__(self):
        try:
            self.close()  # make sure the cursor is closed
        except:  # builtin Exceptions might not exist any more
            pass
