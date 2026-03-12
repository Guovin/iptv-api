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


_migrated_dbs = set()
_migrate_lock = Lock()


def ensure_result_data_schema(db_path):
    """Ensure result_data table exists with expected columns.

    This function will:
    - CREATE TABLE IF NOT EXISTS result_data with the full schema.
    - Query existing columns (if any) and ALTER TABLE to add any missing columns.

    It's safe to call repeatedly and will not remove or change existing columns.
    """
    expected_columns = {
        'id': 'TEXT',
        'url': 'TEXT',
        'headers': 'TEXT',
        'video_codec': 'TEXT',
        'audio_codec': 'TEXT',
        'resolution': 'TEXT',
        'fps': 'REAL',
    }

    if db_path in _migrated_dbs:
        return

    with _migrate_lock:
        if db_path in _migrated_dbs:
            return

        conn = None
        try:
            conn = sqlite3.connect(db_path, timeout=30.0)
            cur = conn.cursor()

            try:
                cur.execute("PRAGMA user_version;")
                row = cur.fetchone()
                user_ver = int(row[0]) if row and row[0] is not None else 0
            except Exception:
                user_ver = 0

            if user_ver >= 1:
                _migrated_dbs.add(db_path)
                return

            try:
                cur.execute(
                    "CREATE TABLE IF NOT EXISTS result_data (id TEXT PRIMARY KEY, url TEXT, headers TEXT, video_codec TEXT, audio_codec TEXT, resolution TEXT, fps REAL)"
                )
            except Exception:
                pass

            try:
                cur.execute("PRAGMA table_info(result_data)")
                rows = cur.fetchall()
                existing = {row[1] for row in rows} if rows else set()
            except Exception:
                existing = set()

            for col, col_type in expected_columns.items():
                if col not in existing:
                    try:
                        cur.execute(f"ALTER TABLE result_data ADD COLUMN {col} {col_type}")
                    except Exception:
                        pass

            try:
                cur.execute("PRAGMA user_version = 1;")
            except Exception:
                pass

            conn.commit()

            _migrated_dbs.add(db_path)
        except Exception:
            try:
                if conn:
                    conn.rollback()
            except Exception:
                pass
        finally:
            try:
                if conn:
                    conn.close()
            except Exception:
                pass
