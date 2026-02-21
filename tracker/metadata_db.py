import sqlite3
import os
import logging
from tracker.config import DB_PATH

class MetadataDB:
    def __init__(self):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS files (
            path TEXT PRIMARY KEY,
            name TEXT,
            size INTEGER,
            created_at REAL,
            modified_at REAL,
            accessed_at REAL,
            access_count INTEGER DEFAULT 0,
            is_deleted INTEGER DEFAULT 0
        )
        """)
        self.conn.commit()

    # ---------- BASIC FETCH ----------

    def get_all_files(self):
        rows = self.conn.execute(
            "SELECT * FROM files WHERE is_deleted = 0 ORDER BY modified_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]

    def get_recent_files(self):
        rows = self.conn.execute("""
            SELECT * FROM files
            WHERE is_deleted = 0 AND accessed_at IS NOT NULL
            ORDER BY accessed_at DESC
            LIMIT 20
        """).fetchall()
        return [dict(r) for r in rows]

    def increment_access_count(self, path):
        self.conn.execute("""
            UPDATE files
            SET access_count = access_count + 1,
                accessed_at = strftime('%s','now')
            WHERE path = ?
        """, (path,))
        self.conn.commit()

    # ---------- 🔥 METADATA SEARCH ----------

    def search_by_metadata(self, filters):
        query = "SELECT * FROM files WHERE is_deleted = 0"
        params = []

        # ACTION FIELD
        field = "created_at"
        if filters["action"] == "opened":
            field = "accessed_at"
            query += " AND accessed_at IS NOT NULL"
        elif filters["action"] == "modified":
            field = "modified_at"

        # DATE RANGE
        if filters["date_from"]:
            query += f" AND {field} >= ?"
            params.append(filters["date_from"])

        if filters["date_to"]:
            query += f" AND {field} <= ?"
            params.append(filters["date_to"])

        # FILE TYPE
        if filters["file_type"]:
            query += " AND name LIKE ?"
            params.append(f"%.{filters['file_type']}")

        logging.info(f"SQL → {query} | {params}")

        rows = self.conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]
