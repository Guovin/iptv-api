import json
import os
import sqlite3
from threading import Lock


_schema_lock = Lock()
_write_lock = Lock()
_migrated_dbs = {}

_RESULT_DATA_SCHEMA = (
    "CREATE TABLE IF NOT EXISTS result_data ("
    "id TEXT PRIMARY KEY, url TEXT, headers TEXT, video_codec TEXT, "
    "audio_codec TEXT, resolution TEXT, fps REAL)"
)

_RESULT_DATA_COLUMNS = {
    "id": "TEXT",
    "url": "TEXT",
    "headers": "TEXT",
    "video_codec": "TEXT",
    "audio_codec": "TEXT",
    "resolution": "TEXT",
    "fps": "REAL",
}


def _configure_connection(conn):
    conn.execute("PRAGMA busy_timeout=30000")
    conn.execute("PRAGMA synchronous=NORMAL")
    return conn


def get_db_connection(db_path):
    db_dir = os.path.dirname(db_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
    return _configure_connection(sqlite3.connect(db_path, timeout=30.0))


def return_db_connection(db_path, conn):
    if conn is None:
        return
    try:
        if conn.in_transaction:
            conn.rollback()
    finally:
        conn.close()


def ensure_result_data_schema(db_path):
    try:
        signature = (os.stat(db_path).st_dev, os.stat(db_path).st_ino)
    except OSError:
        signature = None
    if signature is not None and _migrated_dbs.get(db_path) == signature:
        return

    with _schema_lock:
        try:
            signature = (os.stat(db_path).st_dev, os.stat(db_path).st_ino)
        except OSError:
            signature = None
        if signature is not None and _migrated_dbs.get(db_path) == signature:
            return

        conn = get_db_connection(db_path)
        try:
            cursor = conn.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("BEGIN IMMEDIATE")
            cursor.execute(_RESULT_DATA_SCHEMA)
            cursor.execute("PRAGMA table_info(result_data)")
            existing = {row[1] for row in cursor.fetchall()}
            for column, column_type in _RESULT_DATA_COLUMNS.items():
                if column not in existing:
                    cursor.execute(f"ALTER TABLE result_data ADD COLUMN {column} {column_type}")
            cursor.execute("PRAGMA user_version=1")
            conn.commit()
            stat_result = os.stat(db_path)
            _migrated_dbs[db_path] = (stat_result.st_dev, stat_result.st_ino)
        except Exception:
            conn.rollback()
            raise
        finally:
            return_db_connection(db_path, conn)


def replace_result_data(db_path, rows):
    ensure_result_data_schema(db_path)
    values = [
        (
            str(item.get("id")),
            item.get("url"),
            json.dumps(item.get("headers"), ensure_ascii=False) if item.get("headers") else None,
            item.get("video_codec"),
            item.get("audio_codec"),
            item.get("resolution"),
            item.get("fps"),
        )
        for item in rows
        if item.get("id") is not None and item.get("url")
    ]

    with _write_lock:
        conn = get_db_connection(db_path)
        try:
            conn.execute("BEGIN IMMEDIATE")
            conn.execute("DELETE FROM result_data")
            conn.executemany(
                "INSERT INTO result_data "
                "(id, url, headers, video_codec, audio_codec, resolution, fps) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                values,
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            return_db_connection(db_path, conn)
