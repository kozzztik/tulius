from threading import local
import time


class LocalCounter(local):
    def __init__(self):
        self.clear()
    
    def clear(self):
        self.exec_time = 0
        self.exec_count = 0
        self.temlate_time = 0
        self.template_db_time = 0
        self.template_db_count = 0
        self.rendering_template = False


local_counter = LocalCounter()


def templates_decorator(f):
    def wrapper(*args, **kwargs):
        starttime = int(time.clock() * 1000)
        local_counter.rendering_template = True
        try:
            result = f(*args, **kwargs)
        finally:
            local_counter.rendering_template = False
            end_time = int(time.clock() * 1000)
            local_counter.temlate_time += end_time - starttime
        return result
    return wrapper


class CursorWrapper:
    def __init__(self, cursor, db):
        self.cursor = cursor
        self.db = db
        
    WRAP_ERROR_ATTRS = frozenset(
        ['fetchone', 'fetchmany', 'fetchall', 'nextset'])
    
    def execute(self, sql, params=None):
        self.db.validate_no_broken_transaction()
        self.db.set_dirty()
        starttime = int(time.clock() * 1000)
        try:
            with self.db.wrap_database_errors:
                if params is None:
                    return self.cursor.execute(sql)
                else:
                    return self.cursor.execute(sql, params)
        finally:
            end_time = int(time.clock() * 1000)
            local_counter.exec_count += 1
            local_counter.exec_time += end_time - starttime
    
    def executemany(self, sql, param_list):
        self.db.validate_no_broken_transaction()
        self.db.set_dirty()
        starttime = int(time.clock() * 1000)
        try:
            with self.db.wrap_database_errors:
                return self.cursor.executemany(sql, param_list)
        finally:
            end_time = int(time.clock() * 1000)
            local_counter.exec_count += 1
            local_counter.exec_time += end_time - starttime
    
    def callproc(self, procname, params=None):
        self.db.validate_no_broken_transaction()
        self.db.set_dirty()
        starttime = int(time.clock() * 1000)
        try:

            with self.db.wrap_database_errors:
                if params is None:
                    return self.cursor.callproc(procname)
                else:
                    return self.cursor.callproc(procname, params)
        finally:
            end_time = int(time.clock() * 1000)
            local_counter.exec_count += 1
            local_counter.exec_time += end_time - starttime

            
    def __getattr__(self, attr):
        cursor_attr = getattr(self.cursor, attr)
        if attr in CursorWrapper.WRAP_ERROR_ATTRS:
            return self.db.wrap_database_errors(cursor_attr)
        else:
            return cursor_attr

    def __iter__(self):
        return iter(self.cursor)


def cursor_exec_decorator(f):
    def wrapper(*args, **kwargs):
        starttime = int(time.clock() * 1000)
        try:
            result = f(*args, **kwargs)
        finally:
            end_time = int(time.clock() * 1000)
            if local_counter.rendering_template:
                local_counter.template_db_count += 1
                local_counter.template_db_time += end_time - starttime
            else:
                local_counter.exec_count += 1
                local_counter.exec_time += end_time - starttime
        return result
    return wrapper
