from __future__ import annotations

import sqlite3
from contextlib import closing
from pathlib import Path


class Database:
    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def init(self) -> None:
        with closing(sqlite3.connect(self.db_path)) as conn:
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
