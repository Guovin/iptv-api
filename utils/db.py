import sqlite3
from threading import Lock


class SQLitePool:
    def __init__(self, db_path, pool_size=5, timeout=30.0):
        self.db_path = db_path
        self.pool_size = pool_size
        self.pool = []
        self.lock = Lock()
        self.timeout = timeout
        for _ in range(pool_size):
            self.pool.append(self._create_connection())

    def _create_connection(self):
        conn = sqlite3.connect(self.db_path, timeout=self.timeout, check_same_thread=False)
        try:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")
            conn.execute("PRAGMA busy_timeout = 30000;")
        except Exception:
            pass
        return conn

    def get_connection(self):
        with self.lock:
            if self.pool:
                return self.pool.pop()
            else:
                return self._create_connection()

    def return_connection(self, conn):
        if conn is None:
            return
        with self.lock:
            try:
                if len(self.pool) < self.pool_size:
                    self.pool.append(conn)
                else:
                    conn.close()
            except Exception:
                try:
                    conn.close()
                except Exception:
                    pass

    def close_all(self):
        with self.lock:
            while self.pool:
                conn = self.pool.pop()
                try:
                    conn.close()
                except Exception:
                    pass


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
