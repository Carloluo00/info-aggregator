from __future__ import annotations

import json
import sqlite3
from contextlib import closing
from pathlib import Path

from app.models import Source


class Database:
    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def init(self) -> None:
        with closing(sqlite3.connect(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS sent_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_url TEXT NOT NULL,
                    item_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    link TEXT NOT NULL,
                    published TEXT,
                    sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(source_url, item_id)
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS sources (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    source_type TEXT NOT NULL CHECK(source_type IN ('rss', 'web')),
                    url TEXT NOT NULL,
                    enabled INTEGER NOT NULL DEFAULT 1,
                    fetch_interval_seconds INTEGER NULL,
                    selectors_json TEXT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS app_settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def has_item(self, source_url: str, item_id: str) -> bool:
        with closing(sqlite3.connect(self.db_path)) as conn:
            cursor = conn.execute(
                "SELECT 1 FROM sent_items WHERE source_url = ? AND item_id = ? LIMIT 1",
                (source_url, item_id),
            )
            return cursor.fetchone() is not None

    def add_item(
        self,
        source_url: str,
        item_id: str,
        title: str,
        link: str,
        published: str | None = None,
    ) -> bool:
        with closing(sqlite3.connect(self.db_path)) as conn:
            try:
                conn.execute(
                    """
                    INSERT INTO sent_items (source_url, item_id, title, link, published)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (source_url, item_id, title, link, published),
                )
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False

    def list_sources(self, enabled_only: bool = False) -> list[Source]:
        query = """
            SELECT id, name, source_type, url, enabled, fetch_interval_seconds, selectors_json
            FROM sources
        """
        params: tuple[object, ...] = ()
        if enabled_only:
            query += " WHERE enabled = 1"
        query += " ORDER BY id ASC"
        with closing(sqlite3.connect(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(query, params).fetchall()
        return [self._row_to_source(row) for row in rows]

    def add_source(
        self,
        name: str,
        source_type: str,
        url: str,
        enabled: bool = True,
        fetch_interval_seconds: int | None = None,
        selectors: dict | None = None,
    ) -> int:
        selectors_json = json.dumps(selectors, ensure_ascii=False) if selectors else None
        with closing(sqlite3.connect(self.db_path)) as conn:
            cursor = conn.execute(
                """
                INSERT INTO sources (
                    name, source_type, url, enabled, fetch_interval_seconds, selectors_json
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    name,
                    source_type,
                    url,
                    1 if enabled else 0,
                    fetch_interval_seconds,
                    selectors_json,
                ),
            )
            conn.commit()
            return int(cursor.lastrowid)

    def get_source(self, source_id: int) -> Source | None:
        with closing(sqlite3.connect(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                """
                SELECT id, name, source_type, url, enabled, fetch_interval_seconds, selectors_json
                FROM sources WHERE id = ?
                """,
                (source_id,),
            ).fetchone()
        if row is None:
            return None
        return self._row_to_source(row)

    def update_source(
        self,
        source_id: int,
        *,
        name: str,
        source_type: str,
        url: str,
        enabled: bool,
        fetch_interval_seconds: int | None,
        selectors: dict | None,
    ) -> bool:
        selectors_json = json.dumps(selectors, ensure_ascii=False) if selectors else None
        with closing(sqlite3.connect(self.db_path)) as conn:
            cursor = conn.execute(
                """
                UPDATE sources
                SET name = ?, source_type = ?, url = ?, enabled = ?,
                    fetch_interval_seconds = ?, selectors_json = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    name,
                    source_type,
                    url,
                    1 if enabled else 0,
                    fetch_interval_seconds,
                    selectors_json,
                    source_id,
                ),
            )
            conn.commit()
            return cursor.rowcount > 0

    def delete_source(self, source_id: int) -> bool:
        with closing(sqlite3.connect(self.db_path)) as conn:
            cursor = conn.execute("DELETE FROM sources WHERE id = ?", (source_id,))
            conn.commit()
            return cursor.rowcount > 0

    def toggle_source(self, source_id: int, enabled: bool) -> bool:
        with closing(sqlite3.connect(self.db_path)) as conn:
            cursor = conn.execute(
                "UPDATE sources SET enabled = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (1 if enabled else 0, source_id),
            )
            conn.commit()
            return cursor.rowcount > 0

    def get_setting(self, key: str, default: str | None = None) -> str | None:
        with closing(sqlite3.connect(self.db_path)) as conn:
            row = conn.execute(
                "SELECT value FROM app_settings WHERE key = ?",
                (key,),
            ).fetchone()
        if row is None:
            return default
        return str(row[0])

    def set_setting(self, key: str, value: str) -> None:
        with closing(sqlite3.connect(self.db_path)) as conn:
            conn.execute(
                """
                INSERT INTO app_settings (key, value) VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
                """,
                (key, value),
            )
            conn.commit()

    def import_rss_urls_if_needed(self, rss_urls: list[str]) -> int:
        if not rss_urls:
            return 0
        with closing(sqlite3.connect(self.db_path)) as conn:
            count = conn.execute("SELECT COUNT(1) FROM sources").fetchone()[0]
            if count > 0:
                return 0
            inserted = 0
            for idx, url in enumerate(rss_urls, start=1):
                conn.execute(
                    """
                    INSERT INTO sources (name, source_type, url, enabled)
                    VALUES (?, 'rss', ?, 1)
                    """,
                    (f"RSS Source {idx}", url),
                )
                inserted += 1
            conn.commit()
            return inserted

    @staticmethod
    def _row_to_source(row: sqlite3.Row) -> Source:
        selectors_json = row["selectors_json"]
        selectors = json.loads(selectors_json) if selectors_json else None
        return Source(
            id=int(row["id"]),
            name=str(row["name"]),
            source_type=str(row["source_type"]),
            url=str(row["url"]),
            enabled=bool(row["enabled"]),
            fetch_interval_seconds=row["fetch_interval_seconds"],
            selectors=selectors,
        )
