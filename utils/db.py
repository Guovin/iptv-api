import sqlite3
from threading import Lock


class SQLitePool:
    def __init__(self, db_path, pool_size=5):
        self.db_path = db_path
        self.pool_size = pool_size
        self.pool = []
        self.lock = Lock()
        for _ in range(pool_size):
            self.pool.append(self._create_connection())

    def _create_connection(self):
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def get_connection(self):
        with self.lock:
            if self.pool:
                return self.pool.pop()
            else:
                return self._create_connection()

    def return_connection(self, conn):
        with self.lock:
            if len(self.pool) < self.pool_size:
                self.pool.append(conn)
            else:
                conn.close()


db_pools = {}


def get_db_pool(db_path):
    if db_path not in db_pools:
        db_pools[db_path] = SQLitePool(db_path)
    return db_pools[db_path]


def get_db_connection(db_path):
    pool = get_db_pool(db_path)
    return pool.get_connection()


def return_db_connection(db_path, conn):
    pool = get_db_pool(db_path)
    pool.return_connection(conn)
